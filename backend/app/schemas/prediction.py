from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    id: int = Field(..., ge=1)


class AnomalyCategory(BaseModel):
    score: float
    explanation: str
    top_features: list[str]


class RiskThresholds(BaseModel):
    warning: float
    high: float


class PredictionResponse(BaseModel):
    id: int
    store_name: str

    risk_score: float
    status: str

    thresholds: RiskThresholds

    price_anomaly: AnomalyCategory
    review_anomaly: AnomalyCategory
    information_anomaly: AnomalyCategory

    overall_explanation: str