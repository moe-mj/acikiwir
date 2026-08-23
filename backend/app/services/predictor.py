from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import joblib
import numpy as np
import pandas as pd
import shap
from google import genai
from google.genai import types

from app.schemas.prediction import (
    AnomalyCategory,
    PredictionRequest,
    PredictionResponse,
)
from app.services.preprocessing import build_numeric_features

GEMINI_MODEL = "gemini-3.5-flash"

MODEL_PATH = Path("app/model/model_bundle.joblib")
CSV_PATH = Path("data/synthetic_data.csv")

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

class Predictor:
    def __init__(self, model_path: Path = MODEL_PATH, csv_path: Path = CSV_PATH):
        self.model_path = model_path
        self.csv_path = csv_path

        self.bundle = None
        self.model = None
        self.preprocessor = None
        self.explainer = None
        self.store_data = None

        self._load_model()
        self._load_store_data()

    def _load_model(self) -> None:
        if not self.model_path.exists():
            return

        self.bundle = joblib.load(self.model_path)
        self.model = self.bundle["model"]

        if hasattr(self.model, "named_steps"):
            self.preprocessor = self.model.named_steps["preprocessor"]
            xgb_model = self.model.named_steps["xgb"]
        else:
            self.preprocessor = self.bundle["preprocessor"]
            xgb_model = self.model

        try:
            xgb_model.set_params(device="cpu", tree_method="hist")
        except Exception:
            pass

        self.explainer = shap.TreeExplainer(
            xgb_model
        )

    def _load_store_data(self) -> None:
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Dataset tidak ditemukan: {self.csv_path}")

        df = pd.read_csv(self.csv_path)
        df["id"] = (pd.to_numeric(df["id"], errors="raise").astype(int))

        self.store_data = (df.set_index("id", drop=False))

    @property
    def is_loaded(self) -> bool:
        return (
            self.bundle is not None
            and self.store_data is not None
        )

    def _get_store(self, store_id: int) -> pd.DataFrame:
        store_id = int(store_id)

        if store_id not in self.store_data.index:
            raise ValueError(f"Toko dengan ID {store_id} tidak ditemukan.")

        return self.store_data.loc[[store_id]].copy()

    @staticmethod
    def _get_feature_group(feature_name: str) -> str:
        name = feature_name.lower()
        price_keywords = [
            "price",
            "product_price",
            "category_median_price",
            "price_ratio",
            "price_deviation",
            "rating_price",
        ]

        if any(keyword in name for keyword in price_keywords):
            return "price"

        review_keywords = [
            "review",
            "tfidf",
            "exclamation",
            "question",
            "digit",
            "uppercase",
            "url",
            "spam",
        ]

        if any(keyword in name for keyword in review_keywords):
            return "review"

        return "information"

    @staticmethod
    def _clean_feature_name(feature_name: str) -> str:
        name = feature_name
        prefixes = [
            "num__",
            "word_tfidf__",
            "char_tfidf__",
        ]

        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):]

        return name.strip()

    @staticmethod
    def _translate_feature(feature_name: str) -> str:
        mapping = {
            "five_star_ratio":
                "proporsi ulasan bintang lima yang tidak wajar",
            "res_five_star_ratio":
                "proporsi ulasan bintang lima yang tidak wajar",
            "res_uppercase_count":
                "penggunaan huruf kapital berlebihan pada ulasan",
            "price_deviation":
                "perbedaan harga produk yang mencolok dibandingkan harga pasaran",
            "res_price_deviation":
                "perbedaan harga produk yang mencolok dibandingkan harga pasaran",
            "res_cancellation_rate":
                "tingkat pembatalan pesanan yang tinggi",
            "res_review_rate_1h":
                "lonjakan masuknya ulasan dalam waktu singkat",
            "res_spam_signal":
                "pola ulasan yang menyerupai aktivitas spam",
            "res_log_store_age":
                "umur toko yang relatif masih baru",
            "res_log_orders":
                "lonjakan jumlah pesanan dalam 24 jam terakhir",
            "category_median_price":
                "ketidaksesuaian harga dengan harga umum pada kategori produk",
            "res_url_count":
                "penyematan banyak tautan pada ulasan",
            "res_exclamation_count":
                "penggunaan tanda seru secara berlebihan pada ulasan",
            "res_question_count":
                "penggunaan tanda tanya yang tidak wajar pada ulasan",
            "res_digit_count":
                "penggunaan angka yang tidak biasa pada ulasan",
            "average_rating":
                "nilai rating toko",
            "store_age_days":
                "umur toko",
            "cancellation_rate":
                "tingkat pembatalan pesanan",
            "caps_ratio":
                "proporsi penggunaan huruf kapital pada ulasan",
            "product_price":
                "harga produk",
            "price_ratio":
                "perbandingan harga produk dengan harga umum kategorinya",
            "res_price_ratio_to_median":
                "perbandingan harga produk dengan harga umum kategorinya",
            "total_reviews":
                "jumlah total ulasan",
            "five_star_reviews_last_24h":
                "jumlah ulasan bintang lima dalam 24 jam terakhir",
            "orders_last_24h":
                "jumlah pesanan dalam 24 jam terakhir",
            "reviews_last_1h":
                "jumlah ulasan dalam satu jam terakhir",
        }

        cleaned_name = feature_name.replace("res_", "").strip()

        return mapping.get(
            feature_name,
            mapping.get(
                cleaned_name,
                cleaned_name
                .replace("_", " ")
                .strip(),
            ),
        )

    def _calculate_anomaly_categories(self, feature_names, shap_values) -> dict[str, AnomalyCategory]:
        rows = []

        for feature_name, shap_value in zip(feature_names, shap_values):
            shap_value = float(shap_value)
            cleaned_name = (self._clean_feature_name(feature_name))

            rows.append(
                {
                    "name": cleaned_name,
                    "group": self._get_feature_group(
                        feature_name
                    ),
                    "shap": shap_value,
                    "abs_shap": abs(shap_value),
                }
            )

        total_abs_shap = (
            sum(
                row["abs_shap"]
                for row in rows
            )
            or 1.0
        )

        grouped = {
            "price": [],
            "review": [],
            "information": [],
        }

        for row in rows:
            grouped[
                row["group"]
            ].append(row)

        group_labels = {
            "price": "Harga",
            "review": "Ulasan",
            "information": "Informasi Toko",
        }

        results = {}

        for group_name, group_rows in grouped.items():
            group_abs_shap = sum(row["abs_shap"] for row in group_rows)

            score = (group_abs_shap / total_abs_shap) * 100
            group_rows.sort(key=lambda x: x["abs_shap"], reverse=True)
            top_rows = group_rows[:5]

            top_features = [row["name"] for row in top_rows]

            if top_rows:
                parts = []
                for row in top_rows[:3]:
                    arah = (
                        "meningkatkan"
                        if row["shap"] > 0
                        else "menurunkan"
                    )

                    translated = (
                        self._translate_feature(
                            row["name"]
                        )
                    )

                    parts.append(
                        f"'{translated}' {arah} risiko"
                    )

                explanation = (
                    f"Faktor {group_labels[group_name]} "
                    f"menyumbang {score:.1f}% dari total indikasi. "
                    f"Yang paling berpengaruh: "
                    + ", ".join(parts)
                    + "."
                )

            else:
                explanation = (
                    f"Tidak ada kontribusi signifikan "
                    f"dari faktor {group_labels[group_name]}."
                )

            results[group_name] = AnomalyCategory(
                score=round(
                    score,
                    2,
                ),
                explanation=explanation,
                top_features=top_features,
            )

        return results

    def _generate_llm_explanation(self, risk_score: float, status: str, top_features: list[dict]) -> str:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY tidak ditemukan di environment.")
        
        client = genai.Client(api_key=api_key)
        reasons = []
        for row in top_features:
            description = (
                self._translate_feature(
                    row["name"]
                )
            )

            reasons.append(f"- {description}")

        reasons_text = "\n".join(reasons)

        prompt = f"""
            Anda adalah asisten yang menjelaskan hasil
            deteksi fraud toko online kepada pengguna awam.

            HASIL DETEKSI:
            Skor risiko: {risk_score:.2f}%
            Status: {status}

            FAKTOR UTAMA YANG MENINGKATKAN RISIKO:
            {reasons_text}

            TUGAS:
            Buat penjelasan singkat dalam 2-3 kalimat
            yang menjelaskan hasil deteksi kepada pengguna.

            ATURAN:
            1. Gunakan bahasa Indonesia yang natural dan mudah dipahami.
            2. Jangan menyebut SHAP.
            3. Jangan menyebut feature.
            4. Jangan menyebut variabel.
            5. Jangan menyebut model machine learning.
            6. Jangan menyebut XGBoost.
            7. Jangan mengarang data yang tidak diberikan.
            8. Hubungkan faktor-faktor tersebut dengan potensi risiko bagi pembeli.
            9. Jangan hanya mengulang daftar faktor.
            10. Jadikan semua faktor menjadi satu penjelasan yang koheren.
            11. Jika status SAFE, jangan mengatakan toko pasti aman.
            12. Jika status SAFE, jelaskan bahwa sistem tidak menemukan indikasi kuat.
            13. Jika status WARNING atau HIGH, jelaskan mengapa sistem menjadi waspada.
            14. Jangan memberikan saran finansial atau hukum.
            15. Hanya keluarkan teks penjelasan.
            16. Jangan menggunakan bullet point.
            17. Jangan memberikan judul.
            18. Hindari penggunaan kata ganti orang. Buat seobjektif mungkin. 

            Contoh gaya yang diinginkan:

            "Toko ini memiliki tingkat risiko yang rendah karena
            sistem tidak menemukan pola aktivitas yang cukup kuat
            untuk menunjukkan adanya perilaku mencurigakan.
            Beberapa pola pada harga dan aktivitas ulasan juga
            terlihat masih berada dalam kondisi yang wajar."

            Sekarang buat penjelasan berdasarkan data yang diberikan.
            """

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
            ),
        )

        if response is None:
            raise RuntimeError("Gemini ga bales.")

        text = getattr(response, "text", None)

        if not text:
            raise RuntimeError("Gemini kosong.")

        return text.strip()

    def _generate_fallback_explanation(self, risk_score: float, status: str, top_features: list[dict]) -> str:
        if status == "SAFE":
            return (
                f"Toko ini memiliki skor risiko "
                f"{risk_score:.2f}%. "
                f"Sistem tidak menemukan pola yang cukup kuat "
                f"untuk menunjukkan adanya aktivitas mencurigakan."
            )
        translated_reasons = []
        for row in top_features:
            translated = (
                self._translate_feature(
                    row["name"]
                )
            )
            translated_reasons.append(
                translated
            )

        if not translated_reasons:

            return (
                f"Toko ini memiliki skor risiko "
                f"{risk_score:.2f}% dan sistem menemukan "
                f"beberapa pola yang meningkatkan tingkat kewaspadaan."
            )

        if len(translated_reasons) == 1:
            reasons_text = translated_reasons[0]
        elif len(translated_reasons) == 2:
            reasons_text = (
                f"{translated_reasons[0]} "
                f"dan {translated_reasons[1]}"
            )
        else:
            reasons_text = (
                f"{', '.join(translated_reasons[:-1])}, "
                f"dan {translated_reasons[-1]}"
            )

        return (
            f"Toko ini memiliki skor risiko "
            f"{risk_score:.2f}%. "
            f"Sistem menjadi lebih waspada karena terdapat "
            f"{reasons_text}."
        )

    def predict(self, payload: PredictionRequest) -> PredictionResponse:
        frame = self._get_store(payload.id)
        numeric_extra = build_numeric_features(frame)
        for column in numeric_extra.columns:
            if column not in frame.columns:
                frame[column] = (numeric_extra[column])

        frame = additional_features(frame)
        transformed = (self.preprocessor.transform(frame))

        risk_probability = float(self.model.predict_proba(frame)[0, 1])
        risk_score = (risk_probability * 100)

        thresholds = self.bundle["thresholds"]
        warning_threshold = float(thresholds["warning"])
        high_threshold = float(thresholds["high"])

        if risk_probability < warning_threshold:
            status = "SAFE"
        elif risk_probability < high_threshold:
            status = "WARNING"
        else:
            status = "HIGH"

        shap_values = (
            self.explainer.shap_values(
                transformed
            )
        )

        if isinstance(shap_values, list,):
            shap_values = shap_values[-1]

        shap_row = shap_values[0]
        feature_names = (self.preprocessor .get_feature_names_out())

        categories = (
            self._calculate_anomaly_categories(
                feature_names,
                shap_row,
            )
        )

        all_features = []
        for feature_name, shap_value in zip(feature_names, shap_row):
            shap_value = float(shap_value)
            all_features.append(
                {
                    "name": self._clean_feature_name(
                        feature_name
                    ),
                    "shap": shap_value,
                    "abs_shap": abs(
                        shap_value
                    ),
                }
            )

        positive_features = [
            feature
            for feature in all_features
            if feature["shap"] > 0
        ]

        positive_features.sort(
            key=lambda x: x["shap"],
            reverse=True,
        )

        top_overall = (
            positive_features[:3]
        )


        if top_overall:
            try:
                overall_explanation = (
                    self._generate_llm_explanation(
                        risk_score=risk_score,
                        status=status,
                        top_features=top_overall,
                    )
                )
            except Exception as e:

                print(f"[Gemini ERROR] {type(e).__name__}: {e}")

                overall_explanation = (
                    self._generate_fallback_explanation(
                        risk_score=risk_score,
                        status=status,
                        top_features=top_overall,
                    )
                )

        else:
            overall_explanation = (
                f"Toko ini memiliki skor risiko "
                f"{risk_score:.2f}%. "
                f"Sistem tidak menemukan faktor "
                f"yang secara kuat meningkatkan "
                f"tingkat risikonya."
            )

        return PredictionResponse(
            id=payload.id,
            store_name=str(frame["store_name"].iloc[0]),

            risk_score=round(
                risk_score,
                2,
            ),

            status=status,

            thresholds={
                "warning": round(warning_threshold * 100, 2),
                "high": round(high_threshold * 100, 2),
            },

            price_anomaly=categories["price"],
            review_anomaly=categories["review"],
            information_anomaly=categories["information"],

            overall_explanation=overall_explanation,
        )