// src/services/api.js
import axios from 'axios';

const API_URL = 'http://localhost:8080';  // your FastAPI URL

export const fetchPredictions = async () => {
  try {
    const response = await axios.get(`${API_URL}/analyze/`);
    return response.data;
  } catch (error) {
    console.error("Error fetching predictions:", error);
    return [];
  }
};
