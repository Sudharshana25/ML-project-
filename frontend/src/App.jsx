import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, 
  LineElement, Title, Tooltip, Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  const [history, setHistory] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [date, setDate] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // 1. Fetch History
    fetch(`${API_BASE}/history`)
      .then(res => res.json())
      .then(data => setHistory(data.points || []))
      .catch(err => console.error("History fetch error:", err));

    // 2. Fetch Accuracy Metrics
    fetch(`${API_BASE}/metrics`)
      .then(res => res.json())
      .then(data => setMetrics(data))
      .catch(err => console.error("Metrics fetch error:", err));
  }, []);

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date }),
      });
      const data = await res.json();
      
      // Store everything including the date string for the chart comparison
      setPrediction({ 
        date: date, 
        value: data.predicted_demand, 
        actual: data.actual_demand,
        temp: data.temperature 
      });
    } catch (err) {
      alert("Prediction failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const chartData = {
    labels: history.map(p => p.date),
    datasets: [
      {
        label: 'Actual Demand (MW)',
        data: history.map(p => p.actual_demand),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        tension: 0.3,
      },
      prediction ? {
        label: 'AI Prediction',
        // This line matches the red dot to the specific date on the X-axis
        data: history.map(p => p.date === prediction.date ? prediction.value : null),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgb(239, 68, 68)',
        pointRadius: 10,
        pointStyle: 'rectRot',
        showLine: false,
      } : null
    ].filter(Boolean)
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8 font-sans">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-800">Electricity Demand Forecaster</h1>
          <p className="text-gray-600">XGBoost Forecasting with Historical Averaging</p>
        </header>

        {/* METRICS SECTION */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white p-4 rounded-xl shadow-sm border-l-4 border-green-500">
            <p className="text-sm text-gray-500 uppercase font-bold">Model Accuracy</p>
            <h3 className="text-2xl font-bold text-gray-800">
              {metrics ? metrics.accuracy_score : "..."}
            </h3>
          </div>
          <div className="bg-white p-4 rounded-xl shadow-sm border-l-4 border-blue-500">
            <p className="text-sm text-gray-500 uppercase font-bold">MAE</p>
            <h3 className="text-2xl font-bold text-gray-800">
              {metrics ? `${metrics.mae.toFixed(2)} MW` : "..."}
            </h3>
          </div>
          <div className="bg-white p-4 rounded-xl shadow-sm border-l-4 border-purple-500">
            <p className="text-sm text-gray-500 uppercase font-bold">RMSE</p>
            <h3 className="text-2xl font-bold text-gray-800">
              {metrics ? `${metrics.rmse.toFixed(2)} MW` : "..."}
            </h3>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="bg-white p-6 rounded-xl shadow-md h-fit">
            <h2 className="text-xl font-semibold mb-4 border-b pb-2">Predict Demand</h2>
            <form onSubmit={handlePredict} className="space-y-4">
              <input 
                type="date" 
                className="w-full rounded-md border-gray-300 p-2 border shadow-sm"
                onChange={(e) => setDate(e.target.value)}
                required
              />
              <button 
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-2 rounded-md font-bold hover:bg-blue-700 disabled:bg-blue-300"
              >
                {loading ? "Processing..." : "Run Forecast"}
              </button>
            </form>

            {prediction && (
              <div className="mt-6 space-y-3">
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg text-center">
                  <p className="text-xs text-green-700 font-bold uppercase">AI Prediction</p>
                  <p className="text-2xl font-bold text-green-900">{prediction.value.toFixed(2)} MW</p>
                </div>
                
                {prediction.actual && (
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg text-center">
                    <p className="text-xs text-blue-700 font-bold uppercase">Actual Demand (CSV)</p>
                    <p className="text-2xl font-bold text-blue-900">{prediction.actual.toFixed(2)} MW</p>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-md">
            <div className="h-[400px]">
              <Line 
                data={chartData} 
                options={{ 
                  responsive: true, 
                  maintainAspectRatio: false,
                  plugins: { legend: { position: 'top' } } 
                }} 
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}