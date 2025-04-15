import React, { useEffect, useState } from 'react';
import { fetchPredictions } from '../services/api';

const Dashboard = () => {
  const [predictions, setPredictions] = useState([]);

  useEffect(() => {
    fetchPredictions()
      .then(response => setPredictions(response.data))
      .catch(error => console.error("Error fetching predictions:", error));
  }, []);

  return (
    <div>
      <h2>Predictions Dashboard</h2>
      <table>
        <thead>
          <tr>
            {predictions.length > 0 && Object.keys(predictions[0]).map((key) => (
              <th key={key}>{key}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {predictions.map((row, index) => (
            <tr key={index}>
              {Object.values(row).map((val, idx) => (
                <td key={idx}>{val}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Dashboard;
