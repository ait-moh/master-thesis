import subprocess
import time
import uvicorn
import numpy as np
import pandas as pd
import tensorflow as tf
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from kafka_consumer import consume_messages

# Load the trained model
model = tf.keras.models.load_model("my_model.h5")

# Initialize FastAPI
app = FastAPI(title="Root Cause Analysis API with Kafka")

# CORS (React needs this!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Root Cause Analysis API is running with Kafka!"}

@app.get("/predict_kafka/")
def predict_from_kafka():
    try:
        # ✅ Step 1: Run producer.py to send fresh data to Kafka
        subprocess.run(["python", "producer.py"], check=True)

        # ✅ Step 2: Wait a short moment to ensure Kafka buffers it
        time.sleep(1)  # You can increase if needed

        # ✅ Step 3: Consume messages from Kafka
        kafka_data = consume_messages()

        if kafka_data.shape[0] < 2:
            return {"error": "Not enough data received from Kafka."}

        # ✅ Step 4: Prepare data for model
        def create_sequences(data, seq_length=2, pred_length=1):
            x = []
            for i in range(len(data) - seq_length - pred_length + 1):
                x.append(data[i:(i + seq_length)])
            return np.array(x, dtype=np.float32)

        X_kafka = create_sequences(kafka_data)

        # ✅ Step 5: Make predictions
        predictions = model.predict(X_kafka, batch_size=1024)

        # ✅ Step 6: Prepare output for React
        predictions_df = pd.DataFrame(predictions.reshape(predictions.shape[0], -1))
        predictions_file = "predictions_kafka.csv"
        predictions_df.to_csv(predictions_file, index=False)

        return predictions_df.to_dict(orient="records")

    except subprocess.CalledProcessError as e:
        return {"error": f"Producer failed: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
