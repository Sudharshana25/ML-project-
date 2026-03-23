import React from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

export default function DemandChart({ points }) {
  const labels = (points || []).map((p) => p.date);
  const data = (points || []).map((p) => p.total_demand);

  const chartData = {
    labels,
    datasets: [
      {
        label: "Total demand (MW)",
        data,
        borderColor: "#2563eb",
        backgroundColor: "rgba(37, 99, 235, 0.15)",
        tension: 0.25,
        fill: true,
        pointRadius: 0,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: true },
      tooltip: { enabled: true },
    },
    scales: {
      x: {
        ticks: {
          maxTicksLimit: 8,
        },
      },
      y: {
        beginAtZero: false,
      },
    },
  };

  return (
    <div className="w-full bg-white rounded-lg border p-4">
      <h2 className="text-sm font-semibold mb-3">Historical Demand Trend</h2>
      <Line data={chartData} options={options} />
    </div>
  );
}

