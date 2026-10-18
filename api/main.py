from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(title="Car Evaluation Prediction API", version="1.0.0")
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ml" / "car_evaluation_model.pkl"
CLASS_LABELS = {"unacc": "Unacceptable", "acc": "Acceptable", "good": "Good", "vgood": "Very Good"}

try:
    model = joblib.load(MODEL_PATH)
except Exception as exc:
    model = None
    model_load_error = exc
else:
    model_load_error = None


class CarEvaluationRequest(BaseModel):
    buying: Literal["vhigh", "high", "med", "low"]
    maint: Literal["vhigh", "high", "med", "low"]
    doors: Literal["2", "3", "4", "5more"]
    persons: Literal["2", "4", "more"]
    lug_boot: Literal["small", "med", "big"]
    safety: Literal["low", "med", "high"]


@app.get("/")
async def home():
    return {"message": "Car Evaluation Prediction API is running", "model_ready": model is not None}


@app.post("/predict")
async def predict_car(request: CarEvaluationRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Prediction model is unavailable.")

    input_data = pd.DataFrame([{
        "buying": request.buying,
        "maint": request.maint,
        "doors": request.doors,
        "persons": request.persons,
        "lug_boot": request.lug_boot,
        "safety": request.safety,
    }])

    try:
        raw_prediction = str(model.predict(input_data)[0])
        prediction = CLASS_LABELS[raw_prediction]
        response = {"prediction": prediction}
        if hasattr(model, "predict_proba"):
            values = model.predict_proba(input_data)[0]
            probabilities = {
                CLASS_LABELS[str(label)]: round(float(value) * 100, 2)
                for label, value in zip(model.classes_, values)
            }
            response["confidence"] = probabilities[prediction]
            response["probabilities"] = probabilities
        return response
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Prediction could not be completed.") from exc
