import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceDot,
  Brush,
} from 'recharts';

function App() {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState('');
  const [results, setResults] = useState([]);
  const [columns, setColumns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [forecastStats, setForecastStats] = useState(null);
  const [inputPreview, setInputPreview] = useState([]);
  const [selectedColumn, setSelectedColumn] = useState(null);

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    setFileName(file.name);
    setLoading(true);

    const reader = new FileReader();
    reader.onload = (e) => {
      const lines = e.target.result.split("\n").filter(Boolean);
      const data = lines.map((line) => line.split(","));
      setInputPreview(data);
    };
    reader.readAsText(file);

    try {
      const response = await axios.post("http://localhost:8080/analyze/", formData);
      setResults(response.data.results);
      setColumns(response.data.columns);
      setSelectedColumn(response.data.columns[0]);

      const allValues = response.data.results.map(r => r.values);
      const stats = {
        mean: [],
        min: [],
        max: [],
      };

      for (let i = 0; i < response.data.columns.length; i++) {
        const col = allValues.map(row => row[i]);
        const mean = col.reduce((a, b) => a + b, 0) / col.length;
        const min = Math.min(...col);
        const max = Math.max(...col);
        stats.mean.push(mean.toFixed(2));
        stats.min.push(min.toFixed(2));
        stats.max.push(max.toFixed(2));
      }

      setForecastStats(stats);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCSV = () => {
    if (results.length === 0) return;

    const headers = ["DateTime", ...columns, "Error", "Status"];
    const csvRows = [
      headers.join(","),
      ...results.map(res =>
        [res.datetime, ...res.values, res.error.toFixed(4), res.anomaly_flag ? "Anomaly" : "Normal"].join(",")
      )
    ];
    const blob = new Blob([csvRows.join("\n")], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "forecast_results.csv";
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const chartData = results.map((res, idx) => ({
    datetime: res.datetime,
    value: res.values[columns.indexOf(selectedColumn)],
    anomaly: res.anomaly_flag,
  }));

  return (
    <div className="app-container">
      <header>
        <h1>Forecast & Anomaly Detector</h1>
      </header>

      <div className="input-group">
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button onClick={handleUpload}>Analyze</button>
      </div>

      {loading && <p className="loading">⏳ Processing... please wait</p>}

      {fileName && <p className="meta"><b>File:</b> {fileName}</p>}

      {inputPreview.length > 1 && (
        <>
          <h3>Original Input Sequence</h3>
          <div className="table-wrapper">
            <table className="styled-table">
              <thead>
                <tr>
                  {inputPreview[0].map((header, idx) => (
                    <th key={idx}>{header}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {inputPreview.slice(1).map((row, idx) => (
                  <tr key={idx}>
                    {row.map((cell, i) => (
                      <td key={i}>{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {results.length > 0 && (
        <>
          <h3>Forecasted Sequence</h3>
          <button onClick={handleDownloadCSV}>⬇️ Download CSV</button>
          <div className="table-wrapper">
            <table className="styled-table">
              <thead>
                <tr>
                  <th>DateTime</th>
                  {columns.map(col => (
                    <th key={col}>{col}</th>
                  ))}
                  <th>Error</th>
                  <th>Status</th>
                </tr>
              </thead>
            <tbody>
  {results.map((res, idx) => (
    <tr key={idx} className={res.anomaly_flag ? 'highlight-row' : ''}>
      <td>{new Date(res.datetime).toLocaleString('sv-SE').replace('T', ' ')}</td>

      {res.values.map((val, i) => {
        const colName = columns[i];
        const topCols = res.top_error_columns || [];
        const isMostAnomalous = res.anomaly_flag && topCols.includes(colName);

        return (
          <td key={i} className={isMostAnomalous ? 'most-anomalous' : ''}>
            {val}{isMostAnomalous ? ' ' : ''}
          </td>
        );
      })}

      {/* ✅ Add these two lines back */}
      <td>{res.error.toFixed(4)}</td>
      <td className={res.anomaly_flag ? "anomaly" : "normal"}>
        {res.anomaly_flag ? 'Anomaly' : 'Normal'}
      </td>
    </tr>
  ))}
</tbody>

            </table>
          </div>

          <h3>📉 Forecast Chart</h3>
          <label htmlFor="column-select">Select Feature:</label>
          <select
            id="column-select"
            value={selectedColumn}
            onChange={(e) => setSelectedColumn(e.target.value)}
          >
            {columns.map((col, i) => (
              <option key={i} value={col}>{col}</option>
            ))}
          </select>

          <div style={{ height: 300, width: '100%' }}>
            <ResponsiveContainer>
              <LineChart data={chartData} margin={{ left: 60, right: 30, top: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="datetime" hide />
                <YAxis domain={['auto', 'auto']} tickFormatter={(val) => val.toFixed(3)} tick={{ fontSize: 10 }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="value" stroke="#00e3ff" dot={false} />
                {chartData.map((entry, index) => (
                  entry.anomaly && <ReferenceDot key={index} x={entry.datetime} y={entry.value} r={5} fill="red" />
                ))}
                <Brush dataKey="datetime" height={30} stroke="#00e3ff" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </>
      )}

      {forecastStats && (
        <div className="summary-box futuristic">
          <h3>📊 Forecasted Sequence Statistics</h3>
          <div className="scroll-box">
            <table className="styled-table">
              <thead>
                <tr>
                  <th>Feature</th>
                  {columns.map((col, i) => <th key={i}>{col}</th>)}
                </tr>
              </thead>
              <tbody>
                <tr><td>Mean</td>{forecastStats.mean.map((v, i) => <td key={i}>{v}</td>)}</tr>
                <tr><td>Min</td>{forecastStats.min.map((v, i) => <td key={i}>{v}</td>)}</tr>
                <tr><td>Max</td>{forecastStats.max.map((v, i) => <td key={i}>{v}</td>)}</tr>
              </tbody>
            </table>
          </div>
        </div>
      )}


    </div>
  );
}

export default App;
