import React, { useEffect, useMemo, useState } from "react";
import DemandChart from "./components/DemandChart.jsx";

const API_BASE_URL = "http://localhost:8000";

export default function App() {
  const [selectedDate, setSelectedDate] = useState("");
  const [predicted, setPredicted] = useState(null);
  const [loading, setLoading] = useState(false);
  const [historyPoints, setHistoryPoints] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    // Load historical demand points once for the chart.
    const loadHistory = async () => {
      try {
        setError("");
        const res = await fetch(`${API_BASE_URL}/history`);
        const json = await res.json();
        setHistoryPoints(Array.isArray(json.points) ? json.points : []);
      } catch (e) {
        setError("Failed to load history for the chart.");
      }
    };
    loadHistory();
  }, []);

  const { minDate, maxDate } = useMemo(() => {
    if (!historyPoints || historyPoints.length === 0) return { minDate: undefined, maxDate: undefined };
    const dates = historyPoints.map((p) => p.date);
    return { minDate: dates[0], maxDate: dates[dates.length - 1] };
  }, [historyPoints]);

  const onPredict = async () => {
    if (!selectedDate) {
      setError("Please select a date.");
      return;
    }

    setLoading(true);
    setError("");
    setPredicted(null);

    try {
      const res = await fetch(`${API_BASE_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date: selectedDate }),
      });

      const json = await res.json();
      if (!res.ok) {
        throw new Error(json?.detail || "Prediction request failed.");
      }

      setPredicted(json.predicted_demand);
    } catch (e) {
      setError(e.message || "Prediction failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-10">
        <h1 className="text-3xl font-bold text-center mb-8">
          Electricity Demand Forecasting System
        </h1>

        <div className="bg-white border rounded-lg p-6 shadow-sm">
          <div className="flex flex-col sm:flex-row gap-4 items-end">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">Select Date</label>
              <input
                type="date"
                className="w-full border rounded-md px-3 py-2"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                min={minDate}
                max={maxDate}
              />
            </div>
            <button
              className="w-full sm:w-auto bg-blue-600 text-white font-medium rounded-md px-5 py-2 hover:bg-blue-700 disabled:opacity-60"
              onClick={onPredict}
              disabled={loading}
            >
              Predict Demand
            </button>
          </div>

          {loading && (
            <div className="mt-5 flex items-center gap-3 text-gray-700">
              <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
              <span>Predicting...</span>
            </div>
          )}

          {error && (
            <div className="mt-4 text-sm text-red-700 bg-red-50 border border-red-200 rounded-md px-3 py-2">
              {error}
            </div>
          )}

          {predicted !== null && !loading && !error && (
            <div className="mt-6 p-4 bg-blue-50 border border-blue-100 rounded-md">
              <div className="text-sm text-blue-900 font-medium">Predicted Electricity Demand</div>
              <div className="text-3xl font-bold text-blue-800">{predicted.toFixed(2)} MW</div>
            </div>
          )}
        </div>

        <div className="mt-8">
          <DemandChart points={historyPoints} />
        </div>
      </div>
    </div>
  );
}

