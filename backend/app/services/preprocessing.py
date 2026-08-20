from __future__ import annotations

import re
import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

RAW_NUMERIC_COLUMNS = [
    "store_age_days",
    "orders_last_24h",
    "cancellations_last_24h",
    "reviews_last_1h",
    "five_star_reviews_last_24h",
    "total_reviews",
    "average_rating",
    "product_price",
    "category_median_price",
]

DERIVED_NUMERIC_FEATURES = [
    "cancellation_rate",
    "review_rate",
    "five_star_ratio",
    "price_deviation",
    "price_ratio",
]

EXTRA_NUMERIC_FEATURES = [
    "review_length",
    "word_count",
    "unique_word_ratio",
    "exclamation_count",
    "question_count",
    "caps_ratio",
    "sentiment_score",
]

ALL_NUMERIC_FEATURES = RAW_NUMERIC_COLUMNS + DERIVED_NUMERIC_FEATURES + EXTRA_NUMERIC_FEATURES

class TextCleaner(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.stemmer = StemmerFactory().create_stemmer()
        self.stopword_remover = (StopWordRemoverFactory().create_stop_word_remover())

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [self._clean(text) for text in X]

    def _clean(self, text):
        if not isinstance(text, str):
            text = ""

        text = text.lower()
        text = re.sub(r"http\S+|www\S+|https\S+", " ", text)
        text = re.sub(r"[^a-z\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        text = self.stopword_remover.remove(text)
        text = self.stemmer.stem(text)

        return text

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            return np.array(["review_text"])

        return np.array(input_features)

def build_numeric_features(df: pd.DataFrame) -> pd.DataFrame:
    numeric = pd.DataFrame(index=df.index)

    for col in RAW_NUMERIC_COLUMNS:
        if col in df.columns:
            numeric[col] = df[col]

    orders = (df.get("orders_last_24h", pd.Series(1, index=df.index)).clip(lower=1))
    cancellations = df.get("cancellations_last_24h", pd.Series(0, index=df.index))
    reviews_1h = df.get("reviews_last_1h", pd.Series(0, index=df.index))
    five_star = df.get("five_star_reviews_last_24h", pd.Series(0, index=df.index))
    total_reviews = df.get("total_reviews", pd.Series(1, index=df.index)).clip(lower=1)
    price = df.get("product_price", pd.Series(0, index=df.index))
    median = df.get("category_median_price", pd.Series(1, index=df.index)).clip(lower=1)

    numeric["cancellation_rate"] = cancellations / orders
    numeric["review_rate"] = reviews_1h / orders
    numeric["five_star_ratio"] = five_star / total_reviews
    numeric["price_deviation"] = (price - median).abs() / median
    numeric["price_ratio"] = price / median
    
    review_text = (
        df["review_text"]
        if "review_text" in df.columns
        else pd.Series("", index=df.index)
    )

    original_text = review_text.fillna("")

    numeric["review_length"] = original_text.str.len()
    numeric["word_count"] = original_text.str.split().str.len()
    numeric["unique_word_ratio"] = original_text.apply(lambda x: (len(set(x.split())) / max(len(x.split()), 1)))
    numeric["exclamation_count"] = (original_text.str.count("!"))
    numeric["question_count"] = (original_text.str.count(r"\?"))
    numeric["caps_ratio"] = original_text.apply(lambda x: (sum(1 for c in x if c.isupper()) / max(len(x), 1)))
    
    positive_words = {
        "bagus",
        "mantap",
        "puas",
        "recommended",
        "oke",
        "keren",
    }

    negative_words = {
        "jelek",
        "kecewa",
        "rusak",
        "tidak",
        "buruk",
        "mengecewakan",
    }

    numeric["sentiment_score"] = (
        original_text.apply(lambda x: (sum(1 for w in x.lower().split() if w in positive_words) 
                                       - sum(1 for w in x.lower().split() if w in negative_words)))
        )

    return numeric