from __future__ import annotations
import os
from functools import lru_cache
from pathlib import Path
from datetime import datetime
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

# Correct import: refers to the filename without .py
from train_model import build_features_for_date, load_or_train_model

BACKEND_DIR = Path(__file__).resolve().parent
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictRequest(BaseModel):
    date: str # Expects YYYY-MM-DD from frontend
    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("date must be in YYYY-MM-DD format")
        return v

class PredictResponse(BaseModel):
    predicted_demand: float

MODEL = None

@app.on_event("startup")
def startup_load_model():
    global MODEL
    MODEL, metrics = load_or_train_model()

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if MODEL is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    features = build_features_for_date(req.date)
    pred = MODEL.predict(features)[0]
    return PredictResponse(predicted_demand=float(pred))

@lru_cache(maxsize=1)
def load_history_df():
    os.chdir(BACKEND_DIR)
    df = pd.read_csv("elect demand.csv")
    df["date"] = pd.to_datetime(df["date_1"], dayfirst=True)
    return df.dropna(subset=["total_demand(mw)"])

@app.get("/history")
def history(start_date: str | None = None, end_date: str | None = None):
    df = load_history_df()
    if start_date:
        df = df[df["date"] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df["date"] <= pd.to_datetime(end_date)]
    
    points = [
        {"date": d.strftime("%Y-%m-%d"), "actual_demand": float(td)}
        for d, td in zip(df["date"], df["total_demand(mw)"])
    ]
    return {"points": points}