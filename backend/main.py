import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import train_model

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BACKEND_DIR = Path(__file__).resolve().parent
MODEL, _ = train_model.load_or_train_model()
DF_RAW = pd.read_csv(BACKEND_DIR / "elect demand.csv")
DF_RAW["date_dt"] = pd.to_datetime(DF_RAW["date_1"], dayfirst=True)

class PredictRequest(BaseModel):
    date: str

@app.get("/metrics")
def get_metrics():
    path = BACKEND_DIR / "metrics.json"
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return {"mae": 0, "rmse": 0, "accuracy_score": "N/A"}

@app.post("/predict")
@app.post("/predict")
def predict(req: PredictRequest):
    # Ensure date is a string in YYYY-MM-DD format for comparison
    target_date_obj = pd.to_datetime(req.date)
    target_date_str = target_date_obj.strftime('%Y-%m-%d')
    
    # 1. Look for exact match in CSV
    match = DF_RAW[DF_RAW["date_dt"] == target_date_obj]
    
    if not match.empty:
        temp = float(match.iloc[0]["temp2_ave(c)"])
        actual = float(match.iloc[0]["total_demand(mw)"])
    else:
        # 2. Temporal Averaging for Future Dates
        history_data = DF_RAW[
            (DF_RAW["date_dt"].dt.month == target_date_obj.month) & 
            (DF_RAW["date_dt"].dt.day == target_date_obj.day)
        ]
        if not history_data.empty:
            temp = float(history_data["temp2_ave(c)"].mean())
        else:
            temp = 25.0 # Fallback
        actual = None

    # 3. Predict using the model
    features = train_model.build_features_for_date(target_date_str, temp)
    prediction = MODEL.predict(features)[0]

    return {
        "predicted_demand": float(prediction),
        "actual_demand": actual,
        "temperature": temp,
        "date": target_date_str # Return the formatted string
    }

@app.get("/history")
def history():
    # Sort by date and take the last 100 days
    df = DF_RAW.sort_values("date_dt").tail(100)
    
    points = []
    for _, row in df.iterrows():
        points.append({
            "date": row["date_dt"].strftime('%Y-%m-%d'), # Match YYYY-MM-DD
            "actual_demand": float(row["total_demand(mw)"])
        })
    return {"points": points}