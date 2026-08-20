from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    fbeta_score,
    make_scorer,
    precision_score,
    precision_recall_curve,
    recall_score,
)
from sklearn.model_selection import (
    RandomizedSearchCV,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from xgboost import XGBClassifier

from app.services.preprocessing import (
    ALL_NUMERIC_FEATURES as ORIGINAL_NUMERIC_FEATURES,
    build_numeric_features,
    TextCleaner,
)

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "synthetic_data.csv"
MODEL_PATH = ROOT / "app" / "model" / "model_bundle.joblib"

RANDOM_STATE = 42

EXTRA_FEATURES = [
    "res_cancellation_rate",
    "res_review_rate_1h",
    "res_five_star_ratio",
    "res_price_ratio_to_median",
    "res_rating_price_interaction",
    "res_log_store_age",
    "res_log_orders",
    "res_log_reviews",
    "res_reviews_per_order",
    "res_five_star_per_review",
    "res_price_deviation",
    "res_spam_signal",
    "res_cancellation_review_ratio",
    "res_review_length",
    "res_review_word_count",
    "res_exclamation_count",
    "res_question_count",
    "res_digit_count",
    "res_uppercase_count",
    "res_url_count",
]


ALL_NUMERIC_FEATURES = (
    ORIGINAL_NUMERIC_FEATURES
    + EXTRA_FEATURES
)

def additional_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    eps = 1e-6
    
    orders = df["orders_last_24h"].fillna(0).clip(lower=1)
    cancellations = df["cancellations_last_24h"].fillna(0)
    reviews_1h = df["reviews_last_1h"].fillna(0)
    five_star = df["five_star_reviews_last_24h"].fillna(0)
    total_reviews = df["total_reviews"].fillna(0).clip(lower=1)
    price = df["product_price"].fillna(0)
    median_price = df["category_median_price"].fillna(0).clip(lower=1)

    df["res_cancellation_rate"] = cancellations / orders
    df["res_review_rate_1h"] = reviews_1h / orders
    df["res_five_star_ratio"] = five_star / total_reviews
    df["res_price_ratio_to_median"] = price / median_price
    df["res_rating_price_interaction"] = df["average_rating"].fillna(0) * df["res_price_ratio_to_median"]
    df["res_log_store_age"] = np.log1p(df["store_age_days"].fillna(0).clip(lower=0))
    df["res_log_orders"] = np.log1p(df["orders_last_24h"].fillna(0).clip(lower=0))
    df["res_log_reviews"] = np.log1p(df["total_reviews"].fillna(0).clip(lower=0))
    df["res_reviews_per_order"] = reviews_1h / orders
    df["res_five_star_per_review"] = five_star / total_reviews
    df["res_price_deviation"] = (price - median_price).abs() / median_price
    df["res_spam_signal"] = df["res_review_rate_1h"] * df["res_five_star_ratio"]
    df["res_cancellation_review_ratio"] = df["res_cancellation_rate"] / (df["res_review_rate_1h"] + eps)

    text = df["review_text"].fillna("").astype(str)
    df["res_review_length"] = text.str.len()
    df["res_review_word_count"] = text.str.split().str.len()
    df["res_exclamation_count"] = text.str.count("!")
    df["res_question_count"] = text.str.count(r"\?")
    df["res_digit_count"] = text.str.count(r"\d")
    df["res_uppercase_count"] = text.apply(lambda x: sum(c.isupper() for c in x))
    df["res_url_count"] = (text.str.count(r"https?://|www\."))
    
    return df

def create_preprocessor():
    word_text_pipeline = Pipeline([
        (
            "clean",
            TextCleaner(),
        ),
        (
            "tfidf",
            TfidfVectorizer(
                max_features=2000,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95,
                sublinear_tf=True,
            ),
        ),
    ])

    char_tfidf = TfidfVectorizer(
        analyzer="char",
        max_features=2000,
        ngram_range=(3, 5),
        min_df=2,
        sublinear_tf=True,
    )

    return ColumnTransformer(
        transformers=[
            (
                "num",
                StandardScaler(),
                ALL_NUMERIC_FEATURES,
            ),
            (
                "word_tfidf",
                word_text_pipeline,
                "review_text",
            ),
            (
                "char_tfidf",
                char_tfidf,
                "review_text",
            ),
        ],
        remainder="drop",
    )

def create_tuned_pipeline():

    pipeline = Pipeline([
        (
            "preprocessor",
            create_preprocessor(),
        ),
        (
            "xgb",
            XGBClassifier(
                objective="binary:logistic",
                eval_metric="aucpr",
                random_state=RANDOM_STATE,
                tree_method="hist",
                device="cuda",
                n_jobs=4,
                verbosity=0,
            ),
        ),
    ])

    param_dist = {
        "xgb__n_estimators": [400, 600, 800, 1000],
        "xgb__max_depth": [3, 4, 5, 6],
        "xgb__learning_rate": [0.02, 0.03, 0.05, 0.08,],
        "xgb__min_child_weight": [1, 3, 5, 8],
        "xgb__gamma": [0, 0.1, 0.3, 0.5,],
        "xgb__reg_alpha": [0, 0.01, 0.1, 0.5],
        "xgb__reg_lambda": [1, 2, 5, 10,],
        "xgb__subsample": [0.75, 0.85, 0.95, 1.0],
        "xgb__colsample_bytree": [0.7, 0.8, 0.9, 1.0,],
        "xgb__scale_pos_weight": [3, 4, 5, 6, 7, 8],
    }

    f2_scorer = make_scorer(fbeta_score, beta=2, zero_division=0)
    search = RandomizedSearchCV(
        pipeline,
        param_distributions=param_dist,
        n_iter=40,
        cv=3,
        scoring=f2_scorer,
        n_jobs=1,
        random_state=RANDOM_STATE,
        verbose=1,
        refit=True,
    )

    return search

def get_threshold_metrics(y_true, probs):
    precisions, recalls, thresholds = precision_recall_curve(y_true, probs)
    precisions = precisions[:-1]
    recalls = recalls[:-1]

    f1_scores = 2.0 * precisions * recalls / (precisions + recalls + 1e-12 )
    f2_scores = 5.0 * precisions * recalls / (4.0 * precisions + recalls + 1e-12 )
    f05_scores = 1.25 * precisions * recalls / (0.25 * precisions + recalls + 1e-12 )

    return {
        "thresholds": thresholds,
        "precisions": precisions,
        "recalls": recalls,
        "f1": f1_scores,
        "f2": f2_scores,
        "f05": f05_scores,
    }


def find_risk_thresholds(y_val, probs):
    metrics = get_threshold_metrics(y_val, probs)

    thresholds = metrics["thresholds"]
    precisions = metrics["precisions"]
    recalls = metrics["recalls"]

    if len(thresholds) == 0:
        raise ValueError("Unable to determine risk thresholds from validation predictions.")

    valid_warning = precisions >= 0.90

    if np.any(valid_warning):
        valid_indices = np.where(valid_warning)[0]
        best_idx = valid_indices[np.argmax(recalls[valid_indices])]
    else:
        best_idx = int(np.argmax(metrics["f2"]))

    warning_threshold = float(thresholds[best_idx])

    valid_high = (thresholds > warning_threshold) & (precisions >= 0.95)

    if np.any(valid_high):
        valid_high_indices = np.where(valid_high)[0]
        high_idx = valid_high_indices[np.argmin(thresholds[valid_high_indices])]
        high_threshold = float(thresholds[high_idx])
    else:
        higher_thresholds = thresholds > warning_threshold

        if np.any(higher_thresholds):
            high_threshold = float(np.min(thresholds[higher_thresholds]))
        else:
            high_threshold = warning_threshold + 1e-6

    if high_threshold <= warning_threshold:
        high_threshold = warning_threshold + 1e-6

    return {
        "warning": warning_threshold,
        "high": high_threshold,
    }

def evaluate_threshold(y_true, probs, threshold):
    predictions = (probs >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, predictions, labels=[0, 1], ).ravel()
    
    return {
        "threshold": threshold,
        "accuracy": accuracy_score(y_true, predictions),
        "precision": precision_score(y_true, predictions, zero_division=0),
        "recall": recall_score(y_true, predictions, zero_division=0),
        "f1": f1_score(y_true, predictions, zero_division=0),
        "false_positive_rate": (fp / max(fp + tn, 1)),
        "false_negative_rate": (fn / max(fn + tp, 1)),
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "tp": tp,
    }


def print_metrics(title, y_true, probs, threshold):
    metrics = evaluate_threshold(y_true, probs, threshold,)
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)

    print(f"Threshold       : {metrics['threshold']:.6f}")
    print(f"Accuracy        : {metrics['accuracy']:.4f}")
    print(f"Precision       : {metrics['precision']:.4f}")
    print(f"Recall          : {metrics['recall']:.4f}")
    print(f"F1              : {metrics['f1']:.4f}")
    print(f"False Positive  : {metrics['false_positive_rate']:.4f}")
    print(f"False Negative  : {metrics['false_negative_rate']:.4f}")
    print(
        f"TN={metrics['tn']} "
        f"FP={metrics['fp']} "
        f"FN={metrics['fn']} "
        f"TP={metrics['tp']}"
    )

    print()
    print(
        classification_report(
            y_true,
            (
                probs >= threshold
            ).astype(int),
            target_names=[
                "normal",
                "anomaly",
            ],
            zero_division=0,
        )
    )

    return metrics

def main():
    df = pd.read_csv(RAW_PATH)
    y = (df["label"].astype(int))

    print()
    print("=" * 60)
    print("DATASET")
    print("=" * 60)

    print(f"Total rows       : {len(df)}")
    print(f"Fraud/anomaly    : {y.sum()} ({y.mean():.2%})")
    print(f"Legitimate       : {(y == 0).sum()} ({(y == 0).mean():.2%})")

    numeric_extra = build_numeric_features(df)
    for col in ORIGINAL_NUMERIC_FEATURES:
        if col not in df.columns:
            df[col] = numeric_extra[col]

    df = additional_features(df)

    missing_features = [col for col in ALL_NUMERIC_FEATURES if col not in df.columns]
    if missing_features:
        raise ValueError("Missing numeric features:\n" + "\n".join(missing_features))

    X_train, X_temp, y_train, y_temp = train_test_split(df, y, test_size=0.30, stratify=y, random_state=RANDOM_STATE)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=RANDOM_STATE)

    print()
    print("=" * 60)
    print("DATA SPLIT")
    print("=" * 60)

    print(f"Train            : {len(X_train)}")
    print(f"Validation       : {len(X_val)}")
    print(f"Test             : {len(X_test)}")

    print()
    print("=" * 60)
    print("TUNING")
    print("=" * 60)

    print("Optimization metric: F2")
    print("Search: 40 candidates x 3 folds ""= 120 fits")

    tuned_pipeline = create_tuned_pipeline()
    tuned_pipeline.fit(X_train, y_train,)
    best_model = tuned_pipeline.best_estimator_

    print()
    print("Best parameters:")
    print(tuned_pipeline.best_params_)

    print()
    print("Best CV F2: {tuned_pipeline.best_score_:.4f}")

    val_probs = best_model.predict_proba(X_val)[:, 1]
    test_probs = best_model.predict_proba(X_test)[:, 1]
    val_pr_auc = average_precision_score(y_val, val_probs)
    test_pr_auc = average_precision_score(y_test, test_probs)

    print()
    print("=" * 60)
    print("PR-AUC")
    print("=" * 60)

    print(f"Validation PR-AUC : {val_pr_auc:.4f}")
    print(f"Test PR-AUC       : {test_pr_auc:.4f}")

    thresholds = find_risk_thresholds(y_val, val_probs)
    warning_threshold = thresholds["warning"]
    high_threshold = thresholds["high"]

    print()
    print("=" * 60)
    print("RISK THRESHOLDS")
    print("=" * 60)
    print(f"Safe       < {warning_threshold:.6f}")
    print(f"Warning    < {high_threshold:.6f}")
    print(f"High       >= {high_threshold:.6f}")

    val_metrics = print_metrics("VALIDATION - WARNING OPERATING POINT", y_val, val_probs, warning_threshold)
    high_val_metrics = print_metrics("VALIDATION - HIGH RISK", y_val, val_probs, high_threshold,)

    test_metrics = print_metrics("FINAL TEST - WARNING OPERATING POINT", y_test, test_probs, warning_threshold)
    high_test_metrics = print_metrics("FINAL TEST - HIGH RISK", y_test, test_probs, high_threshold)

    test_safe = (test_probs < warning_threshold)
    test_warning = ((test_probs >= warning_threshold) & (test_probs < high_threshold))
    test_high = (test_probs >= high_threshold)

    print()
    print("=" * 60)
    print("FINAL TEST RISK DISTRIBUTION")
    print("=" * 60)

    print(f"SAFE      : {test_safe.sum()} ({test_safe.mean():.2%})")
    print(f"WARNING   : {test_warning.sum()} ({test_warning.mean():.2%})")
    print(f"HIGH      : {test_high.sum()} ({test_high.mean():.2%})")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    bundle = {
        "model": best_model,
        "preprocessor": (
            best_model
            .named_steps["preprocessor"]
        ),
        "thresholds": thresholds,
        "features": {
            "numeric": ALL_NUMERIC_FEATURES,
            "extra": EXTRA_FEATURES,
        },
        "metrics": {
            "validation": {
                "pr_auc": val_pr_auc,
                **val_metrics,
            },
            "validation_high": {
                **high_val_metrics,
            },
            "test": {
                "pr_auc": test_pr_auc,
                **test_metrics,
            },
            "test_high": {
                **high_test_metrics,
            },
        },
        "threshold_policy": {
            "warning_target_precision": 0.90,
            "high_target_precision": 0.95,
            "optimization_metric": "F2",
        },
    }

    joblib.dump(bundle, MODEL_PATH)

    print()
    print("=" * 60)
    print("MODEL SAVED")
    print("=" * 60)

    print(MODEL_PATH)


if __name__ == "__main__":
    main()