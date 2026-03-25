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
    date: str # YYYY-MM-DD
    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        datetime.strptime(v, "%Y-%m-%d")
        return v

# Pre-load Model and Dataset for lookups
MODEL, _ = load_or_train_model()
DF_RAW = pd.read_csv(BACKEND_DIR / "elect demand.csv")
DF_RAW["date_dt"] = pd.to_datetime(DF_RAW["date_1"], dayfirst=True)

@app.post("/predict")
def predict(req: PredictRequest):
    target_date = pd.to_datetime(req.date)
    
    # Check if we have historical data for this date to get the REAL temp
    match = DF_RAW[DF_RAW["date_dt"] == target_date]
    
    if not match.empty:
        # Date exists in CSV: Use the recorded temperature
        actual_temp = float(match.iloc[0]["temp2_ave(c)"])
        actual_demand = float(match.iloc[0]["total_demand(mw)"])
    else:
        # Future date: Use a default average temperature
        actual_temp = 27.5 
        actual_demand = None

    features = build_features_for_date(req.date, actual_temp)
    prediction = MODEL.predict(features)[0]

    return {
        "predicted_demand": float(prediction),
        "actual_demand": actual_demand, # Used for UI Comparison
        "temperature": actual_temp
    }

@app.get("/history")
def history():
    # Return last 100 days for the chart
    df = DF_RAW.sort_values("date_dt").tail(100)
    points = [
        {"date": d.strftime("%Y-%m-%d"), "actual_demand": float(td)}
        for d, td in zip(df["date_dt"], df["total_demand(mw)"])
    ]
    return {"points": points}