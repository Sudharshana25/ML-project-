import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const API_BASE = "http://127.0.0.1:8000";

export default function App() {
  const [history, setHistory] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [date, setDate] = useState("");
  const [loading, setLoading] = useState(false);

  // 1. Fetch History on Load
  useEffect(() => {
    fetch(`${API_BASE}/history?start_date=2023-01-01`)
      .then(res => res.json())
      .then(data => setHistory(data.points))
      .catch(err => console.error("History fetch error:", err));
  }, []);

  // 2. Handle Prediction
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
      setPrediction({ date, value: data.predicted_demand });
    } catch (err) {
      alert("Prediction failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  // 3. Prepare Chart Data
  const chartData = {
    labels: history.map(p => p.date),
    datasets: [
      {
        label: 'Actual Demand (MW)',
        data: history.map(p => p.actual_demand),
        borderColor: 'rgb(59, 130, 246)', // Blue
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        tension: 0.3,
      },
      prediction ? {
        label: 'AI Prediction',
        data: history.map(p => p.date === prediction.date ? prediction.value : null),
        borderColor: 'rgb(239, 68, 68)', // Red
        pointRadius: 8,
        pointStyle: 'rectRot',
        showLine: false, // Just show the predicted point
      } : null
    ].filter(Boolean)
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8 font-sans">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-800">Electricity Demand Forecaster</h1>
          <p className="text-gray-600">Analyze historical trends and predict future load</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Panel: Inputs */}
          <div className="bg-white p-6 rounded-xl shadow-md h-fit">
            <h2 className="text-xl font-semibold mb-4 border-b pb-2">Predict Demand</h2>
            <form onSubmit={handlePredict} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Select Date</label>
                <input 
                  type="date" 
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2 border"
                  onChange={(e) => setDate(e.target.value)}
                  required
                />
              </div>
              <button 
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition disabled:bg-blue-300"
              >
                {loading ? "Calculating..." : "Run Forecast"}
              </button>
            </form>

            {prediction && (
              <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-700">Predicted Load for {prediction.date}:</p>
                <p className="text-2xl font-bold text-green-900">{prediction.value.toFixed(2)} MW</p>
              </div>
            )}
          </div>

          {/* Right Panel: Chart */}
          <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-md">
            <h2 className="text-xl font-semibold mb-4 border-b pb-2">Demand Trend (Historical vs Prediction)</h2>
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