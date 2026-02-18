import React, { useEffect, useState } from "react";
import axios from "axios";

const API = process.env.REACT_APP_API_URL || "";

const Pipeline = () => {
  const [status, setStatus] = useState(null);
  const [results, setResults] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);

  const fetchStatus = async () => {
    try {
      const res = await axios.get(`${API}/pipeline/status`);
      const data = res.data;

      setStatus(data.status);
      setIsRunning(data.status === "running");

      if (Array.isArray(data.results)) {
        setResults(data.results);
      } else {
        setResults([]);
      }
    } catch (err) {
      console.error("Error fetching status:", err);
      setError("Failed to load pipeline status");
    }
  };

  const runPipeline = async () => {
    try {
      await axios.post(`${API}/pipeline/run`);
      fetchStatus();
    } catch (err) {
      console.error("Pipeline start failed:", err);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h2>Pipeline</h2>

      <p>Status: {status || "Unknown"}</p>

      <button onClick={runPipeline} disabled={isRunning}>
        {isRunning ? "Running..." : "Run Pipeline"}
      </button>

      {error && <p>{error}</p>}

      <h3>Results</h3>
      <ul>
        {results.map((r, idx) => (
          <li key={idx}>{JSON.stringify(r)}</li>
        ))}
      </ul>
    </div>
  );
};

export default Pipeline;
