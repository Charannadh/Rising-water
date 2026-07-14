import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import joblib

from config import BASE_DIR, DATASET_PATH, MODEL_PATH, MODEL_INFO_PATH


def generate_dataset(path: Path, rows: int = 250) -> None:
    rng = np.random.default_rng(42)
    data = []
    for _ in range(rows):
        water_level = round(float(rng.uniform(20, 95)), 2)
        rainfall = round(float(rng.uniform(5, 80)), 2)
        temperature = round(float(rng.uniform(22, 40)), 2)
        humidity = round(float(rng.uniform(40, 95)), 2)
        river_flow = round(float(rng.uniform(20, 90)), 2)
        soil_moisture = round(float(rng.uniform(25, 85)), 2)
        water_velocity = round(float(rng.uniform(1.2, 4.8)), 2)
        previous_flood_history = int(rng.choice([0, 1, 2, 3], p=[0.7, 0.2, 0.08, 0.02]))

        if water_level > 88 or rainfall > 72 or river_flow > 85 or (water_level > 72 and previous_flood_history > 0):
            label = "Emergency"
        elif water_level > 74 or rainfall > 55 or river_flow > 70 or soil_moisture > 78:
            label = "Danger"
        elif water_level > 60 or rainfall > 35 or river_flow > 50:
            label = "Warning"
        else:
            label = "Normal"

        data.append([water_level, rainfall, temperature, humidity, river_flow, soil_moisture, water_velocity, previous_flood_history, label])

    df = pd.DataFrame(data, columns=["water_level", "rainfall", "temperature", "humidity", "river_flow", "soil_moisture", "water_velocity", "previous_flood_history", "prediction_label"])
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def train_model():
    if not DATASET_PATH.exists():
        generate_dataset(DATASET_PATH)

    df = pd.read_csv(DATASET_PATH)
    df = df.dropna()
    x = df[["water_level", "rainfall", "temperature", "humidity", "river_flow", "soil_moisture", "water_velocity", "previous_flood_history"]]
    y = df["prediction_label"]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=42)

    models = {
        "Random Forest": RandomForestClassifier(n_estimators=120, random_state=42),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=500, random_state=42)),
        "Support Vector Machine": make_pipeline(StandardScaler(), SVC(probability=True, random_state=42)),
    }

    results = {}
    for name, model in models.items():
        model.fit(x_train, y_train)
        preds = model.predict(x_test)
        acc = accuracy_score(y_test, preds)
        results[name] = float(acc)

    best_model_name = max(results, key=results.get)
    best_model = models[best_model_name]
    best_model.fit(x, y)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, MODEL_PATH)

    with MODEL_INFO_PATH.open("w", encoding="utf-8") as handle:
        json.dump({"best_model": best_model_name, "accuracy": results[best_model_name], "results": results}, handle, indent=2)

    print(f"Training complete. Best model: {best_model_name} with accuracy {results[best_model_name]:.2f}")


if __name__ == "__main__":
    train_model()
