# Electricity Demand Forecasting System

Full-stack ML app:
- FastAPI backend
- XGBoost model trained on `elect demand.csv`
- React + Tailwind frontend (Chart.js line chart)

## Project Layout

- `backend/`
  - `main.py` (FastAPI)
  - `train_model.py` (training script)
  - `elect demand.csv` (copied into backend)
  - `requirements.txt`
- `frontend/`
  - React UI + Tailwind + Chart.js

## Backend Setup

1. Create a virtual environment (optional but recommended).
2. Install dependencies:
   - `cd backend`
   - `pip install -r requirements.txt`
3. Train (or load existing `model.pkl`):
   - `python train_model.py`
   - This saves `model.pkl` in `backend/`.
4. Start the API:
   - `uvicorn backend.main:app --reload --port 8000`

API:
- `GET /` -> `{"message": "API is running"}`
- `POST /predict` with:
  - `{"date": "YYYY-MM-DD"}`
- `GET /history` -> `{ "points": [{ "date": "...", "total_demand": ... }, ...] }`

## Frontend Setup

1. Start the backend first (FastAPI on `http://localhost:8000`).
2. Install frontend deps:
   - `cd frontend`
   - `npm install`
3. Run the app:
   - `npm run dev`
4. Open the URL shown in the terminal (typically `http://localhost:5173`).

## Deployment (Optional)

- Backend (Render/Railway): set the start command to `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Frontend (Vercel/Netlify): build with `npm run build` and serve static assets

