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
    """
    Feature engineering exactly as specified in task.md:
      - df['date'] -> datetime
      - df['day'], df['month'], df['weekday']
      - X = [['day','month','weekday']]
      - y = total_demand
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])

    df["day"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["weekday"] = df["date"].dt.weekday

    # Drop rows with missing values in required columns.
    df = df.dropna(subset=["day", "month", "weekday", "total_demand", "date"])

    X = df[["day", "month", "weekday"]]
    y = df["total_demand"]
    return X, y


def load_or_train_model(model_path: str = "model.pkl") -> tuple[XGBRegressor, TrainResult | None]:
    """
    If model.pkl already exists, load it instead of retraining.
    Otherwise train an XGBRegressor and persist it using:
      joblib.dump(model, "model.pkl")
    """
    backend_dir = Path(__file__).resolve().parent
    model_file = backend_dir / model_path

    # Ensure strict relative paths in task.md work:
    #   df = pd.read_csv("elect demand.csv")
    os.chdir(backend_dir)

    if model_file.exists():
        model = joblib.load(model_file)
        return model, None

    # --- DATASET INTEGRATION (STRICT) ---
    df = pd.read_csv("elect demand.csv")

    X, y = _prepare_features(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        train_size=0.8,
        random_state=42,
    )

    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        objective="reg:squarederror",
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))

    # --- MODEL STORAGE (STRICT) ---
    joblib.dump(model, "model.pkl")

    return model, TrainResult(mae=mae, rmse=rmse)


def build_features_for_date(date_str: str) -> pd.DataFrame:
    """
    Convert YYYY-MM-DD into day/month/weekday features compatible with the trained model.
    """
    dt = pd.to_datetime(date_str).to_pydatetime()
    # datetime.weekday(): Monday=0..Sunday=6 (matches pandas dt.weekday())
    return pd.DataFrame(
        [
            {
                "day": dt.day,
                "month": dt.month,
                "weekday": dt.weekday(),
            }
        ]
    )


if __name__ == "__main__":
    model, metrics = load_or_train_model()
    if metrics is not None:
        print(f"Training complete. MAE={metrics.mae:.4f} RMSE={metrics.rmse:.4f}")
    else:
        print("Loaded existing model.pkl")

