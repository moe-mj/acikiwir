from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

RANDOM_STATE = 42

ROWS = 20000
ANOMALY_RATIO = 0.12

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "synthetic_data.csv"

RNG = np.random.default_rng(RANDOM_STATE)

FAKER = Faker("id_ID")
FAKER.seed_instance(RANDOM_STATE)

GENERIC_REVIEWS = [
    "Barang bagus mantap",
    "Barang bagus sesuai deskripsi",
    "Cepat sampai bagus",
    "Mantap recommended",
    "Seller terpercaya",
    "Produk bagus recommended",
    "Kualitas mantap",
    "Barang original bagus",
]

NORMAL_REVIEWS = [
    "Produk sesuai deskripsi dan pengiriman cukup cepat",
    "Kualitas barang bagus, packing rapi",
    "Barang datang aman dan sesuai pesanan",
    "Harga sesuai kualitas produk",
    "Pelayanan penjual cukup responsif",
    "Barang dikirim dengan aman dan sesuai pesanan",
    "Produk berfungsi dengan baik",
    "Pengiriman cukup cepat dan packing aman",
    "Sesuai dengan foto dan deskripsi produk",
    "Barang diterima dalam kondisi baik",
]

MIXED_REVIEWS = [
    "Barang sesuai deskripsi, pengiriman cukup cepat",
    "Produk bagus dan packing rapi",
    "Barang bagus, seller cukup responsif",
    "Pengiriman cepat, kualitas sesuai harga",
    "Produk diterima dengan baik, packing aman",
    "Barang lumayan bagus sesuai harga",
    "Sesuai deskripsi dan pengiriman normal",
    "Kualitas cukup baik, pengiriman aman",
]

def clip(value: float, low: float, high: float) -> float:
    return float(np.clip(value, low, high))

def positive_int(value: float, minimum: int = 0) -> int:
    return int(max(round(value), minimum))

def sample_price_median() -> float:
    value = RNG.lognormal(mean=np.log(175_000), sigma=0.75)
    return clip(value, 30_000, 2_000_000)

def sample_store_age() -> float:
    value = RNG.lognormal(mean=np.log(120), sigma=1.35)
    return clip(value, 0.5, 2500)

def sample_order_volume(store_age: float) -> int:
    age_factor = np.log1p(store_age)
    baseline = np.exp(RNG.normal(loc=np.log(12), scale=1.05)) * (0.75 + 0.28 * age_factor)
    if RNG.random() < 0.08:
        baseline *= RNG.uniform(2.0, 5.0)
    return positive_int(baseline, minimum=1)

def sample_cancellation_rate(suspicious_strength: float) -> float:
    normal_rate = RNG.beta(1.5, 50.0)
    suspicious_rate = RNG.beta(3.0, 8.0)

    rate = normal_rate * (1.0 - suspicious_strength) + suspicious_rate * suspicious_strength

    if RNG.random() < 0.05:
        rate += RNG.uniform(0.02, 0.08)

    return clip(rate, 0.0, 0.65)


def sample_review_rate(suspicious_strength: float) -> float:
    normal_rate = RNG.beta(1.5, 50.0)
    suspicious_rate = RNG.beta(3.5, 8.0)

    rate = normal_rate * (1.0 - suspicious_strength) + suspicious_rate * suspicious_strength

    if RNG.random() < 0.03:
        rate *= RNG.uniform(2.0, 4.0)

    return clip(rate, 0.0, 0.80)


def sample_rating(suspicious_strength: float) -> float:
    normal_rating = 3.8 + 1.1 * RNG.beta(6.0, 2.2)
    suspicious_rating = 4.5 + 0.5 * RNG.beta(8.0, 1.5)

    rating = normal_rating * (1.0 - suspicious_strength) + suspicious_rating * suspicious_strength

    return clip(rating, 3.0, 5.0)

def sample_price_deviation(suspicious_strength: float) -> float:
    normal_deviation = abs(RNG.normal(loc=0.06, scale=0.05))
    suspicious_deviation = abs(RNG.normal(loc=0.45, scale=0.20))

    deviation = normal_deviation * (1.0 - suspicious_strength) + suspicious_deviation * suspicious_strength

    return clip(deviation, 0.0, 2.0)


def apply_price_direction(median: float, deviation: float, suspicious_strength: float) -> float:
    direction_roll = RNG.random()

    if suspicious_strength > 0.5 and direction_roll < 0.8:
        direction = -1.0
    elif direction_roll < 0.5:
        direction = -1.0
    else:
        direction = 1.0

    multiplier = 1.0 + direction * deviation
    return clip(median * multiplier, 5_000, 5_000_000)

def generate_review_text(suspicious_strength: float) -> str:
    roll = RNG.random()

    if suspicious_strength > 0.5 and roll < 0.85:
        count = int(RNG.integers(3, 9))
        return " ".join(RNG.choice(GENERIC_REVIEWS, size=count))

    if suspicious_strength > 0.25 and roll < 0.40:
        count = int(RNG.integers(2, 5))
        parts = []
        for _ in range(count):
            if RNG.random() < 0.7:
                parts.append(RNG.choice(GENERIC_REVIEWS))
            else:
                parts.append(RNG.choice(MIXED_REVIEWS))
        return " ".join(parts)

    if RNG.random() < 0.03:
        count = int(RNG.integers(1, 2))
        return " ".join(RNG.choice(GENERIC_REVIEWS, size=count))

    count = int(RNG.integers(1, 4))
    if RNG.random() < 0.5:
        return " ".join(RNG.choice(NORMAL_REVIEWS, size=count))
    else:
        return " ".join(RNG.choice(MIXED_REVIEWS, size=count))


def generate_suspicious_strength(label: int) -> float:
    if label == 1:
        strength = RNG.beta(4.0, 1.5)
        if RNG.random() < 0.10:
            strength *= RNG.uniform(0.40, 0.75)
    else:
        strength = RNG.beta(1.2, 8.0)
        if RNG.random() < 0.05:
            strength = RNG.uniform(0.25, 0.50)

    return clip(strength, 0.0, 1.0)

def generate_row(id:int, label: int) -> dict:
    suspicious_strength = generate_suspicious_strength(label)

    age = sample_store_age()
    if label == 0 and RNG.random() < 0.10:
        age = RNG.uniform(1, 30)
    if label == 1 and RNG.random() < 0.12:
        age = RNG.uniform(180, 1500)

    orders = sample_order_volume(age)
    if RNG.random() < suspicious_strength * 0.7:
        orders = positive_int(orders * RNG.uniform(1.5, 4.0))
    if label == 0 and RNG.random() < 0.10:
        orders = positive_int(orders * RNG.uniform(1.5, 4.0))
    orders = int(np.clip(orders, 1, 3000))

    cancellation_rate = sample_cancellation_rate(suspicious_strength)
    cancellations = int(RNG.binomial(orders, cancellation_rate))

    review_rate = sample_review_rate(suspicious_strength)
    reviews_1h = int(RNG.poisson(max(0.2, orders * review_rate / 24.0)))
    reviews_1h = int(np.clip(reviews_1h, 0, max(orders * 2, 1)))

    review_24h_rate = clip(review_rate * RNG.uniform(12, 28), 0.01, 0.90)
    reviews_24h = int(RNG.poisson(max(1.0, orders * review_24h_rate)))
    reviews_24h = int(np.clip(reviews_24h, reviews_1h, max(orders * 2, reviews_1h, 1)))

    historical_multiplier = RNG.uniform(1.0, 20.0)
    total_reviews = positive_int(reviews_24h * historical_multiplier)
    total_reviews = max(total_reviews, reviews_24h, 1)
    total_reviews = min(total_reviews, 50_000)

    five_star_rate = 0.55 + 0.38 * suspicious_strength + RNG.normal(0, 0.07)
    five_star_rate = clip(five_star_rate, 0.40, 0.99)
    five_star = int(RNG.binomial(total_reviews, five_star_rate))

    rating = sample_rating(suspicious_strength)

    median = sample_price_median()
    price_deviation = sample_price_deviation(suspicious_strength)
    price = apply_price_direction(median, price_deviation, suspicious_strength)

    review = generate_review_text(suspicious_strength)

    return {
        "id": id,
        "store_name": FAKER.company(),
        "ip_address": FAKER.ipv4(),
        "store_age_days": round(age, 2),
        "orders_last_24h": orders,
        "cancellations_last_24h": cancellations,
        "reviews_last_1h": reviews_1h,
        "five_star_reviews_last_24h": five_star,
        "total_reviews": total_reviews,
        "average_rating": round(rating, 3),
        "product_price": round(price, 2),
        "category_median_price": round(median, 2),
        "review_text": review,
        "label": label,
    }

def main(n: int = ROWS, anomaly_ratio: float = ANOMALY_RATIO):
    n_anomaly = int(n * anomaly_ratio)
    n_legit = n - n_anomaly

    labels = np.array([1] * n_anomaly + [0] * n_legit)
    RNG.shuffle(labels)

    rows = [generate_row(id, int(label)) for id, label in enumerate(labels, start=1)]
    df = pd.DataFrame(rows)

    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_PATH, index=False)

    print(f"Generated {len(df)} rows -> {RAW_PATH}")
    print(df["label"].value_counts().rename(index={0: "legit", 1: "anomaly"}))

    print("\nNumeric summary by label:")
    print(
        df.groupby("label")[
            [
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
        ]
        .mean()
        .rename(index={0: "normal", 1: "anomaly"})
        .round(2)
    )


if __name__ == "__main__":
    main()