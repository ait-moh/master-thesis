import uvicorn
import numpy as np
import pandas as pd
import tensorflow as tf
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from io import StringIO
from sklearn.preprocessing import MinMaxScaler
import joblib
import os
import json

# Constants
INPUT_STEPS = 32
FORECAST_STEPS = 32
MANUAL_PERCENTILE = 90
AMPLIFICATION_FACTOR = 6

# Load models and scalers
current_dir = os.path.dirname(os.path.abspath(__file__))
forecast_model = tf.keras.models.load_model(os.path.join(current_dir, "best_lstm_attention_forecaster.h5"))
detection_model = tf.keras.models.load_model(os.path.join(current_dir, "best_detection_lstm_autoencoder.h5"))
forecast_scaler = joblib.load(os.path.join(current_dir, "forecast_scaler.pkl"))
detection_scaler = joblib.load(os.path.join(current_dir, "detection_scaler.pkl"))

# Load amplification parameters
with open(os.path.join(current_dir, "amplification_params.json")) as f:
    amplification_params = json.load(f)



app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    try:
        content = await file.read()
        df = pd.read_csv(StringIO(content.decode()))
        if 'DateTime' in df.columns:
            df['DateTime'] = pd.to_datetime(df['DateTime'])
            df.set_index('DateTime', inplace=True)
        if 'labels' in df.columns:
            df = df.drop(columns=['labels'])

        scaled_input = forecast_scaler.transform(df.values)
        df_scaled = pd.DataFrame(scaled_input, index=df.index, columns=df.columns)

        if len(df_scaled) < INPUT_STEPS:
            return JSONResponse(content={"error": "Not enough data for forecasting."}, status_code=400)

        input_seq = df_scaled.values[-INPUT_STEPS:]
        input_seq = np.expand_dims(input_seq, axis=0)

        forecast = forecast_model.predict(input_seq, batch_size=128, verbose=1)[0]

        forecast[0]  = forecast[5]
        forecast[1]  = forecast[5]
        forecast[2]  = forecast[5]
        forecast[3]  = forecast[5]
        forecast[4]  = forecast[5]

        denorm_forecast = forecast_scaler.inverse_transform(forecast)
        denorm_df = pd.DataFrame(denorm_forecast, columns=df.columns)

        # Save a copy before amplification
        raw_forecast = denorm_df.copy()

        # Amplify variation
        for col in df.columns:
            if col not in amplification_params:
                continue
            params = amplification_params[col]
            adjusted_ratio = params["adjusted_ratio"]
            mean_val = params["mean_val"]
            denorm_df[col] = mean_val + adjusted_ratio * (denorm_df[col] - mean_val)



        # Detection model
        detection_input = detection_scaler.transform(denorm_df.values)
        detection_input_seq = np.expand_dims(detection_input, axis=0)
        reconstructed = detection_model.predict(detection_input_seq, batch_size=128, verbose=1)[0]

        #reconstruction_errors = np.max(np.abs(detection_input - reconstructed), axis=1)

        # === Compute full reconstruction errors per attribute ===
        full_errors = np.abs(detection_input - reconstructed)  # shape (32, num_features)
        reconstruction_errors = np.max(full_errors, axis=1)
        #max_error_indices = np.argmax(full_errors, axis=1)
        #max_error_columns = [df.columns[i] for i in max_error_indices]

        topk_indices = np.argsort(-full_errors, axis=1)[:, :1]  # shape (32, 3)
        topk_columns = [[df.columns[i] for i in row] for row in topk_indices]


        print(topk_columns)



        reconstruction_errors[0]  = reconstruction_errors[6]
        reconstruction_errors[1]  = reconstruction_errors[6]
        reconstruction_errors[2]  = reconstruction_errors[6]
        reconstruction_errors[3]  = reconstruction_errors[6]
        reconstruction_errors[4]  = reconstruction_errors[6]
        reconstruction_errors[5]  = reconstruction_errors[6]

        threshold = 0.178
        flags = (reconstruction_errors > threshold).astype(np.int32)


        # Timestamp estimation
        if isinstance(df.index[0], pd.Timestamp):
            time_step_minutes = int((df.index[1] - df.index[0]).total_seconds() // 60)
            start_time = df.index[-1] + pd.Timedelta(minutes=time_step_minutes)
            timestamps = [start_time + pd.Timedelta(minutes=i * time_step_minutes) for i in range(FORECAST_STEPS)]
            denorm_df.insert(0, "DateTime", timestamps)
            raw_forecast.insert(0, "DateTime", timestamps)

        results = []
        for i in range(FORECAST_STEPS):
            results.append({
                "datetime": raw_forecast.iloc[i]["DateTime"].isoformat(),
                "values": [float(v) for v in raw_forecast.iloc[i].drop("DateTime").values],
                "anomaly_flag": int(flags[i]),
                "error": float(reconstruction_errors[i]),
                "top_error_columns": topk_columns[i]
            })

        raw_values = raw_forecast.values.tolist()

                # === Apply Upper Bound Heuristic ===
        heuristic_attribute = "530R002D02.TI0037.MEAS" 
        upper_bound = 729

        # Determine sequence-level anomaly flag
        upper_bound_violation = np.any(raw_forecast[heuristic_attribute] > upper_bound)
        detection_violation = np.any(reconstruction_errors > threshold)
        sequence_flag = int(upper_bound_violation or detection_violation)


        return {
            "results": results,
            "threshold": threshold,
            "columns": df.columns.tolist(),
            "raw_forecast": raw_values,
            "sequence_flag": sequence_flag
}


    

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

