import uvicorn
import numpy as np
import pandas as pd
import tensorflow as tf
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse

# Load the trained model
model = tf.keras.models.load_model("my_model.h5")  # Change if needed

# Initialize FastAPI
app = FastAPI(title="Root Cause Analysis API")

# Define input data format
class InputData(BaseModel):
    features: list  # Expects a list of feature values

# Root endpoint
@app.get("/")
def home():
    return {"message": "Root Cause Analysis API is running!"}


@app.get("/predict_csv/")
def predict_from_csv():
    df = pd.read_csv("df_scaled.csv")  # Load CSV data


        # Define sequence and prediction lengths
    sequence_length = 2  # one week (168 hours if data is hourly)
    prediction_length = 1  # predicting the next 24 hours

    # Function to create sequences
    def create_sequences(data, seq_length, pred_length):
        x, y = [], []
        for i in range(len(data) - seq_length - pred_length + 1):
            x.append(data[i:(i + seq_length)])
            y.append(data[(i + seq_length):(i + seq_length + pred_length)])
        return np.array(x, dtype=np.float32), np.array(y, dtype=np.float32)
    # Create sequences
    X, Y = create_sequences(df.values, sequence_length, prediction_length)

    # Split data into training and test sets
    train_size = int(0.7 * len(X))
    X_train, Y_train = X[:train_size], Y[:train_size]
    X_test, Y_test = X[train_size:], Y[train_size:]

    # Ensure X_test has correct shape
    if X_test.shape[0] == 0:
        return {"error": "X_test is empty! Check dataset and sequence length."}

    #X_test = X_test.reshape(-1, sequence_length, X_test.shape[-1])  # Ensure 3D shape

    # Get predictions
    predictions = model.predict(X_test, batch_size=1024)

    # **LIMIT THE OUTPUT SIZE** (First 100 predictions)
    #limited_predictions = predictions[:100]  

    #return {"predictions": limited_predictions.tolist()}
    # **Save predictions to CSV**
    predictions_df = pd.DataFrame(predictions.reshape(predictions.shape[0], -1))  
    predictions_file = "predictions.csv"
    predictions_df.to_csv(predictions_file, index=False)

    return FileResponse(predictions_file, media_type="text/csv", filename="predictions.csv")




# Run the API with Uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
