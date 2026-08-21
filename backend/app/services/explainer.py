from __future__ import annotations

import numpy as np

FEATURE_LABELS = {
    "store_age_days": "store age",
    "orders_last_24h": "order volume",
    "cancellation_rate": "cancellation rate",
    "review_rate": "review rate",
    "review_velocity": "review velocity",
    "five_star_ratio": "five-star review ratio",
    "rating": "rating",
    "price_deviation": "price deviation",
    "price_ratio": "price ratio",
    "review_length": "review length",
    "word_count": "review word count",
    "unique_word_ratio": "unique word ratio",
    "exclamation_count": "exclamation count",
    "question_count": "question count",
    "caps_ratio": "uppercase ratio",
    "sentiment_score": "review sentiment",
    "res_cancellation_rate": "cancellation rate",
    "res_review_rate_1h": "1-hour review rate",
    "res_five_star_ratio": "five-star review ratio",
    "res_price_ratio_to_median": "price ratio to category median",
    "res_rating_price_interaction": "rating-price interaction",
    "res_log_store_age": "log store age",
    "res_log_orders": "log order volume",
    "res_log_reviews": "log review volume",
    "res_reviews_per_order": "reviews per order",
    "res_five_star_per_review": "five-star reviews per review",
    "res_price_deviation": "price deviation",
    "res_spam_signal": "review spam signal",
    "res_cancellation_review_ratio": "cancellation-review ratio",
    "res_review_length": "review length",
    "res_review_word_count": "review word count",
    "res_exclamation_count": "review exclamation count",
    "res_question_count": "review question count",
    "res_digit_count": "review digit count",
    "res_uppercase_count": "review uppercase count",
    "res_url_count": "review URL count",
}


def _clean_feature_name(feature_name: str) -> str:
    name = str(feature_name)
    if "__" in name:
        _, name = name.split("__", 1)

    return name


def _feature_label(feature_name: str) -> str:
    original = str(feature_name)
    clean_name = _clean_feature_name(original)

    if clean_name in FEATURE_LABELS:
        return FEATURE_LABELS[clean_name]
    if original.startswith("word_tfidf__"):
        token = clean_name.replace("_", " ")
        return f"review wording: '{token}'"
    if original.startswith("char_tfidf__"):
        token = clean_name.replace("_", " ")
        return f"review pattern: '{token}'"
    return clean_name.replace("_", " ")


def make_reasons(feature_names, shap_values, top_k=3):

    values = np.asarray(shap_values, dtype=float).reshape(-1)
    names = list(feature_names)

    ranked = np.argsort(np.abs(values))[::-1][:top_k]

    reasons = []

    for idx in ranked:
        value = values[idx]
        direction = (
            "increases"
            if value > 0
            else "decreases"
        )

        label = _feature_label(names[idx])

        reasons.append(
            f"{label} {direction} the fraud risk"
        )

    return reasons


def shap_rows(feature_names, shap_values, top_k=5):
    values = np.asarray(shap_values, dtype=float).reshape(-1)
    names = list(feature_names)

    ranked = np.argsort(np.abs(values))[::-1][:top_k]
    rows = []

    for idx in ranked:
        value = float(values[idx])

        rows.append(
            {
                "feature": str(names[idx]),
                "label": _feature_label(names[idx]),
                "shap_value": value,
                "impact": (
                    "higher_risk"
                    if value > 0
                    else "lower_risk"
                ),
            }
        )

    return rows