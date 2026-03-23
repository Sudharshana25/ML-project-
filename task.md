Build a complete full-stack Machine Learning web application for Electricity Demand Forecasting.

PROJECT OVERVIEW:
The application predicts electricity demand (in MW) using historical data. It should allow users to select a date and get the predicted electricity demand using a trained XGBoost model.

TECH STACK:
- Backend: FastAPI (Python)
- Machine Learning: XGBoost, Scikit-learn
- Frontend: React with Tailwind CSS
- Data Processing: Pandas, NumPy
- Model Storage: Joblib
- Charts: Chart.js or Recharts

--------------------------------------
DATASET INTEGRATION (VERY IMPORTANT)
--------------------------------------
A dataset file named "elect demand.csv" is provided in the project root.

The dataset contains:
- date (datetime column)
- total_demand (target variable in MW)

STRICT INSTRUCTIONS:
- DO NOT generate synthetic or random data
- MUST use the uploaded file "elect demand.csv"
- Load dataset using:
    df = pd.read_csv("elect demand.csv")

DATA PREPROCESSING:
1. Convert date column:
    df['date'] = pd.to_datetime(df['date'])

2. Perform feature engineering:
    df['day'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['weekday'] = df['date'].dt.weekday

3. Define:
    X = df[['day', 'month', 'weekday']]
    y = df['total_demand']

4. Handle missing values if any.

--------------------------------------
MODEL BUILDING
--------------------------------------
1. Use XGBRegressor
2. Split dataset:
    train_test_split (80% train, 20% test)

3. Train model:
    model.fit(X_train, y_train)

4. Evaluate using:
    - MAE
    - RMSE

5. Save model:
    joblib.dump(model, "model.pkl")

6. If model.pkl already exists, load it instead of retraining.

--------------------------------------
BACKEND (FastAPI)
--------------------------------------
Create a FastAPI application with:

1. Endpoint:
   GET /
   → returns "API is running"

2. Endpoint:
   POST /predict

   Input JSON:
   {
     "date": "YYYY-MM-DD"
   }

   Backend should:
   - Convert date into day, month, weekday
   - Pass to model
   - Return prediction

   Output JSON:
   {
     "predicted_demand": float
   }

3. Add:
   - Input validation
   - Error handling
   - CORS middleware for frontend

--------------------------------------
FRONTEND (React + Tailwind)
--------------------------------------
Build a modern UI with:

1. Title:
   "Electricity Demand Forecasting System"

2. Input:
   - Date picker

3. Button:
   - "Predict Demand"

4. Display:
   - Predicted electricity demand
   - Loading spinner
   - Error message (if any)

5. Graph:
   - Show historical demand trend using Chart.js or Recharts

6. UX Features:
   - Auto-convert date into required format
   - Clean responsive design

--------------------------------------
PROJECT STRUCTURE
--------------------------------------
backend/
  main.py
  model.pkl
  elect demand.csv
  requirements.txt

frontend/
  src/
  components/
  pages/

--------------------------------------
DEPLOYMENT (OPTIONAL BUT INCLUDE CODE)
--------------------------------------
- Backend: Render / Railway
- Frontend: Vercel / Netlify

--------------------------------------
OUTPUT REQUIREMENTS
--------------------------------------
Generate complete working code for:

1. ML training script
2. FastAPI backend
3. React frontend
4. requirements.txt
5. README with setup instructions

--------------------------------------
FINAL CONDITION
--------------------------------------
Ensure full working flow:

User selects date → frontend sends request → backend processes → model predicts → result displayed in UI

Ensure code is clean, modular, and well-commented.