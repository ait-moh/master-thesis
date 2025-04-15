// src/App.js
import React, { useState } from 'react';
import { fetchPredictions } from './services/api';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend
);

function App() {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);

  // Manual trigger function
  const getPredictions = async () => {
    setLoading(true);
    try {
      const data = await fetchPredictions();
      setPredictions(data);
    } catch (error) {
      console.error("Error fetching predictions:", error);
    } finally {
      setLoading(false);
    }
  };

  // Prepare data for the chart
  const prepareChartData = () => {
    if (predictions.length === 0) return {};

    const labels = predictions.map((_, index) => index + 1);
    const firstKey = Object.keys(predictions[0])[0];

    return {
      labels,
      datasets: [
        {
          label: firstKey,
          data: predictions.map((item) => item[firstKey]),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.3,
        },
      ],
    };
  };

  const computeStats = () => {
    if (!predictions || predictions.length === 0 || !predictions[0]) return null;
  
    const firstKey = Object.keys(predictions[0])[0];
    if (!firstKey) return null;
  
    const values = predictions.map(item => item[firstKey]);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const avg = (values.reduce((a, b) => a + b, 0) / values.length).toFixed(4);
  
    return { min, max, avg };
  };
  

  const stats = computeStats();

  return (
    <div className="App" style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>🚀 Real-Time Predictions Dashboard</h1>

      {/* Button to manually trigger prediction */}
      <button onClick={getPredictions} disabled={loading}>
        {loading ? '⏳ Loading...' : '🚀 Get Predictions'}
      </button>

      {/* Stats */}
      {stats && (
        <div style={{ marginTop: '20px' }}>
          <h2>Statistics (First Feature)</h2>
          <p>Minimum: {stats.min}</p>
          <p>Maximum: {stats.max}</p>
          <p>Average: {stats.avg}</p>
        </div>
      )}

      {/* Chart */}
      {predictions.length > 0 && (
        <div style={{ width: '80%', margin: 'auto' }}>
          <h2>Predictions Over Time</h2>
          <Line data={prepareChartData()} />
        </div>
      )}

      {/* Table */}
      {predictions.length > 0 && (
        <div style={{ marginTop: '40px' }}>
          <h2>Raw Predictions Data</h2>
          <table border="1" cellPadding="5" style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th>Index</th>
                {Object.keys(predictions[0]).map((key) => (
                  <th key={key}>{key}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {predictions.map((row, index) => (
                <tr key={index}>
                  <td>{index}</td>
                  {Object.values(row).map((value, idx) => (
                    <td key={idx}>{Number(value).toFixed(4)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;
