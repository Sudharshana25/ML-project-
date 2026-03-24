from __future__ import annotations
import os
from pathlib import Path
from dataclasses import dataclass
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

@dataclass(frozen=True)
class TrainResult:
    mae: float
    rmse: float

def _prepare_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    df = df.copy()
    # Use date_1 and specify dayfirst=True for DD/MM/YYYY format
    df["date"] = pd.to_datetime(df["date_1"], dayfirst=True)
    df["day"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["weekday"] = df["date"].dt.weekday

    # Ensure we use the exact column name 'total_demand(mw)'
    df = df.dropna(subset=["day", "month", "weekday", "total_demand(mw)", "date"])
    X = df[["day", "month", "weekday"]]
    y = df["total_demand(mw)"]
    return X, y

def load_or_train_model(model_path: str = "model.pkl") -> tuple[XGBRegressor, TrainResult | None]:
    backend_dir = Path(__file__).resolve().parent
    model_file = backend_dir / model_path
    os.chdir(backend_dir)

    if model_file.exists():
        model = joblib.load(model_file)
        return model, None

    df = pd.read_csv("elect demand.csv")
    X, y = _prepare_features(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=4, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    joblib.dump(model, "model.pkl")
    return model, TrainResult(mae=mae, rmse=rmse)

def build_features_for_date(date_str: str) -> pd.DataFrame:
    dt = pd.to_datetime(date_str)
    return pd.DataFrame([{"day": dt.day, "month": dt.month, "weekday": dt.weekday()}])

if __name__ == "__main__":
    model, metrics = load_or_train_model()
    if metrics:
        print(f"Training complete. MAE={metrics.mae:.4f} RMSE={metrics.rmse:.4f}")