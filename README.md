# Master Thesis Project

A full-stack application featuring a **frontend UI** and a **backend API** for time-series forecasting and anomaly detection using LSTM models.

---

## 🧭 Table of Contents

- [Overview](#overview)  
- [Prerequisites](#prerequisites)  
- [Installation](#installation)  
- [Running Locally](#running-locally)  
- [Using Docker Compose](#using-docker-compose)  
- [Backend File Breakdown](#backend-file-breakdown)  
- [Contributing](#contributing)

---

## Overview

This project provides:
- A **React** (or similar) frontend in the `frontend/` folder
- A **Python Flask**-based backend in `backend/app.py`, serving:
  - Time-series forecasting (`best_lstm_attention_forecaster.h5`)
  - Anomaly detection (`best_detection_lstm_autoencoder.h5`)
- A `docker-compose.yml` to run both services together

---

## Prerequisites

- Python 3.8+  
- Node.js and npm / Yarn  
- Docker & Docker Compose (optional, for containerization)

---

## Installation

### Backend

```bash
cd backend
pip install -r requirements.txt
