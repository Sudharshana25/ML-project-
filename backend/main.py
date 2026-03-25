from __future__ import annotations
import os
import pandas as pd
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from train_model import load_or_train_model, build_features_for_date

BACKEND_DIR = Path(__file__).resolve().parent
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictRequest(BaseModel):
    date: str
    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str):
        datetime.strptime(v, "%Y-%m-%d")
        return v

# Pre-load Model and CSV for fast lookup
MODEL, _ = load_or_train_model()
DF_LOOKUP = pd.read_csv(BACKEND_DIR / "elect demand.csv")
DF_LOOKUP["date_parsed"] = pd.to_datetime(DF_LOOKUP["date_1"], dayfirst=True)

@app.post("/predict")
def predict(req: PredictRequest):
    target_date = pd.to_datetime(req.date)
    
    # 1. Look for this date in the CSV to get the "Real" temperature
    match = DF_LOOKUP[DF_LOOKUP["date_parsed"] == target_date]
    
    if not match.empty:
        # Use historical temperature for accuracy
        actual_temp = float(match.iloc[0]["temp2_ave(c)"])
        actual_demand = float(match.iloc[0]["total_demand(mw)"])
    else:
        # Future date: use a default temperature (e.g., 28 degrees)
        actual_temp = 28.0 
        actual_demand = None

    # 2. Build features and Predict
    features = build_features_for_date(req.date, actual_temp)
    pred = MODEL.predict(features)[0]

    return {
        "predicted_demand": float(pred),
        "actual_demand": actual_demand, # Return actual to show "VS" in UI
        "temperature_used": actual_temp,
        "error_margin": abs(float(pred) - actual_demand) if actual_demand else None
    }

@app.get("/history")
def history():
    # Show only the last 100 days for a cleaner chart
    df = DF_LOOKUP.sort_values("date_parsed").tail(100)
    return {
        "points": [
            {"date": d.strftime("%Y-%m-%d"), "actual_demand": float(td)}
            for d, td in zip(df["date_parsed"], df["total_demand(mw)"])
        ]
    }