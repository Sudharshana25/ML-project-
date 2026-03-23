from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from datetime import datetime

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    # Pydantic v2
    from pydantic import field_validator  # type: ignore

    _HAS_FIELD_VALIDATOR = True
except ImportError:  # pragma: no cover
    # Pydantic v1
    from pydantic import validator  # type: ignore

    _HAS_FIELD_VALIDATOR = False

from .train_model import build_features_for_date, load_or_train_model


BACKEND_DIR = Path(__file__).resolve().parent


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo/development; tighten in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictRequest(BaseModel):
    date: str

    if _HAS_FIELD_VALIDATOR:

        @field_validator("date")  # type: ignore[misc]
        @classmethod
        def validate_date(cls, v: str) -> str:
            # Enforce YYYY-MM-DD (task requirement).
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError as e:
                raise ValueError("date must be in YYYY-MM-DD format") from e
            return v

    else:  # pragma: no cover

        @validator("date")  # type: ignore[misc]
        def validate_date(cls, v: str) -> str:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError as e:
                raise ValueError("date must be in YYYY-MM-DD format") from e
            return v


class PredictResponse(BaseModel):
    predicted_demand: float


MODEL = None


@app.on_event("startup")
def startup_load_model() -> None:
    global MODEL
    # load_or_train_model uses relative paths as required by task.md.
    MODEL, metrics = load_or_train_model()
    if metrics is not None:
        # Simple visibility during startup logs.
        print(f"Model trained. MAE={metrics.mae:.4f} RMSE={metrics.rmse:.4f}")
    else:
        print("Model loaded from existing model.pkl")


@app.get("/")
def root() -> str:
    return "API is running"


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    if MODEL is None:
        raise HTTPException(status_code=500, detail="Model not loaded yet.")

    try:
        features = build_features_for_date(req.date)
        pred = MODEL.predict(features)[0]
        return PredictResponse(predicted_demand=float(pred))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {e}") from e


def _ensure_backend_cwd() -> None:
    # Ensures strict `pd.read_csv("elect demand.csv")` works reliably.
    os.chdir(BACKEND_DIR)


@lru_cache(maxsize=1)
def load_history_df() -> pd.DataFrame:
    _ensure_backend_cwd()
    df = pd.read_csv("elect demand.csv")
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["date", "total_demand"]).sort_values("date")
    return df


@app.get("/history")
def history(start_date: str | None = None, end_date: str | None = None):
    """
    Returns historical demand points for charting.
    Optional query params: start_date, end_date (YYYY-MM-DD).
    """
    df = load_history_df()

    if start_date is not None:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            df = df[df["date"] >= start_dt]
        except ValueError as e:
            raise HTTPException(status_code=400, detail="start_date must be YYYY-MM-DD") from e

    if end_date is not None:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            df = df[df["date"] <= end_dt]
        except ValueError as e:
            raise HTTPException(status_code=400, detail="end_date must be YYYY-MM-DD") from e

    points = [
        {"date": d.strftime("%Y-%m-%d"), "total_demand": float(td)}
        for d, td in zip(df["date"], df["total_demand"])
    ]
    return {"points": points}

