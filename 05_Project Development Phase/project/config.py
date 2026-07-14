import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database.db"
MODEL_PATH = BASE_DIR / "models" / "model.pkl"
DATASET_PATH = BASE_DIR / "dataset" / "river_flood_data.csv"
MODEL_INFO_PATH = BASE_DIR / "models" / "model_info.json"
