import json
import joblib
from pathlib import Path

from config import MODEL_PATH, MODEL_INFO_PATH


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Model file is missing. Train the model first.")
    return joblib.load(MODEL_PATH)


def predict_risk(input_data):
    model = load_model()
    features = [
        input_data["water_level"],
        input_data["rainfall"],
        input_data["temperature"],
        input_data["humidity"],
        input_data["river_flow"],
        input_data["soil_moisture"],
        input_data["water_velocity"],
        input_data["previous_flood_history"],
    ]
    prediction = model.predict([features])[0]
    confidence = max(model.predict_proba([features])[0])
    risk_level = {
        "Normal": "Safe",
        "Warning": "Warning",
        "Danger": "High Risk",
        "Emergency": "Danger",
    }.get(prediction, "Safe")
    return {"prediction": prediction, "confidence": round(float(confidence), 3), "risk_level": risk_level}
