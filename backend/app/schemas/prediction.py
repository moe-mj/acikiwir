from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    id: int = Field(..., ge=1)


class AnomalyCategory(BaseModel):
    score: float
    explanation: str
    top_features: list[str]


class PredictionResponse(BaseModel):
    id: int
    store_name: str

    risk_score: float
    status: str

    price_anomaly: AnomalyCategory
    review_anomaly: AnomalyCategory
    information_anomaly: AnomalyCategory

    overall_explanation: str