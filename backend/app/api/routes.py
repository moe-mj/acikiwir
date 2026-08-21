from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
)
from app.services.predictor import Predictor


router = APIRouter(prefix="/api")

MODEL_PATH = Path("app/model/model_bundle.joblib")
CSV_PATH = Path("data/synthetic_data.csv")

predictor = Predictor(model_path=MODEL_PATH,csv_path=CSV_PATH)


@router.post("/predict", response_model=PredictionResponse,)
def predict(payload: PredictionRequest):
    if not predictor.is_loaded:
        raise HTTPException(
            status_code=503,
            detail=(
                "Model atau dataset belum tersedia."
            ),
        )

    try:
        return predictor.predict(payload)

    except ValueError as exc:
        message = str(exc)

        if "tidak ditemukan" in message:
            raise HTTPException(
                status_code=404,
                detail=message,
            ) from exc

        raise HTTPException(
            status_code=400,
            detail=message,
        ) from exc