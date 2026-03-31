import os
import joblib
import json
import numpy as np
import pandas as pd
from pathlib import Path
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

# Setup Paths
BACKEND_DIR = Path(__file__).resolve().parent
DATA_PATH = BACKEND_DIR / "elect demand.csv"
MODEL_PATH = BACKEND_DIR / "model.pkl"
METRICS_PATH = BACKEND_DIR / "metrics.json"

def _prepare_features(df: pd.DataFrame):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date_1"], dayfirst=True)
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["weekday"] = df["date"].dt.weekday
    features = ["year", "month", "day", "weekday", "temp2_ave(c)"]
    df = df.dropna(subset=features + ["total_demand(mw)"])
    return df[features], df["total_demand(mw)"]

def load_or_train_model():
    if MODEL_PATH.exists() and METRICS_PATH.exists():
        model = joblib.load(MODEL_PATH)
        with open(METRICS_PATH, "r") as f:
            metrics = json.load(f)
        return model, metrics

    print("🚀 Training XGBoost Model...")
    df = pd.read_csv(DATA_PATH)
    X, y = _prepare_features(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    model = XGBRegressor(n_estimators=1000, learning_rate=0.03, max_depth=6, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    
    metrics = {
        "mae": mae, 
        "rmse": rmse, 
        "accuracy_score": f"{max(0, 100 - mape):.2f}%"
    }
    
    joblib.dump(model, MODEL_PATH)
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f)
        
    return model, metrics

def build_features_for_date(date_str, temp):
    dt = pd.to_datetime(date_str)
    return pd.DataFrame([{
        "year": dt.year, "month": dt.month, "day": dt.day,
        "weekday": dt.weekday(), "temp2_ave(c)": temp
    }])

if __name__ == "__main__":
    if MODEL_PATH.exists(): os.remove(MODEL_PATH)
    load_or_train_model()
    print("✅ Model & Metrics saved successfully.")