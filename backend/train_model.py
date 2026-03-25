from __future__ import annotations
import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

@dataclass(frozen=True)
class TrainResult:
    mae: float
    rmse: float

def _prepare_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    df = df.copy()
    # Ensure correct date parsing
    df["date"] = pd.to_datetime(df["date_1"], dayfirst=True)
    
    # Extract features including Year and Temperature
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["weekday"] = df["date"].dt.weekday

    features = ["year", "month", "day", "weekday", "temp2_ave(c)"]
    
    # Clean data
    df = df.dropna(subset=features + ["total_demand(mw)"])
    
    X = df[features]
    y = df["total_demand(mw)"]
    return X, y

def load_or_train_model(model_path: str = "model.pkl") -> tuple[XGBRegressor, TrainResult | None]:
    backend_dir = Path(__file__).resolve().parent
    model_file = backend_dir / model_path
    
    if model_file.exists():
        return joblib.load(model_file), None

    # Load dataset from the same folder
    df = pd.read_csv(backend_dir / "elect demand.csv")
    X, y = _prepare_features(df)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    # Improved model parameters to reduce error
    model = XGBRegressor(
        n_estimators=1000, 
        learning_rate=0.03, 
        max_depth=6, 
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    
    joblib.dump(model, model_file)
    return model, TrainResult(mae=mae, rmse=rmse)

def build_features_for_date(date_str: str, temp: float) -> pd.DataFrame:
    dt = pd.to_datetime(date_str)
    return pd.DataFrame([{
        "year": dt.year,
        "month": dt.month,
        "day": dt.day,
        "weekday": dt.weekday(),
        "temp2_ave(c)": temp
    }])