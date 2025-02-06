# Install missing dependencies if needed
# pip install adtk seaborn matplotlib pandas yfinance

import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import seaborn as sns

from adtk.data import validate_series
from adtk.visualization import plot
from adtk.detector import (
    ThresholdAD, QuantileAD, InterQuartileRangeAD, 
    GeneralizedESDTestAD, PersistAD, VolatilityShiftAD
)

# 🔹 Fix: Override Matplotlib Style
plt.style.use("ggplot")  # Use ggplot instead of seaborn-whitegrid

# 🔹 Step 1: Load CSV and clean column names
df = pd.read_csv("temperature.csv")
df.columns = df.columns.str.strip()  # Remove leading/trailing spaces
df = df[["Year", "Mean"]]  # Keep only required columns

# 🔹 Step 2: Convert "Year" column to datetime and set as index
df["Year"] = pd.to_datetime(df["Year"], format="%Y-%m")
df = df.set_index("Year")

# 🔹 Step 3: Select "Mean" column for time-series analysis
s_train = df["Mean"]

# 🔹 Step 4: Validate the time series format
s_train = validate_series(s_train)

# 🔹 Step 5: Plot the original data
plot(s_train)
plt.show()
# =============================
# 🔹 Threshold Anomaly Detection
# =============================
threshold_ad = ThresholdAD(high=0.75, low=-0.5)
anomalies = threshold_ad.detect(s_train)
plot(s_train, anomaly=anomalies, anomaly_color="red", anomaly_tag="marker")
plt.show()

# =============================
# 🔹 Quantile Anomaly Detection
# =============================
quantile_ad = QuantileAD(high=0.99, low=0.01)
anomalies = quantile_ad.fit_detect(s_train)
plot(s_train, anomaly=anomalies, anomaly_color="red", anomaly_tag="marker")
plt.show()

# =========================================
# 🔹 Inter Quartile Range Anomaly Detection
# =========================================
iqr_ad = InterQuartileRangeAD(c=1.5)
anomalies = iqr_ad.fit_detect(s_train)
plot(s_train, anomaly=anomalies, anomaly_color="red", anomaly_tag="marker")
plt.show()

# ============================================
# 🔹 Generalized Extreme Studentized Deviate (ESD) Test
# ============================================
esd_ad = GeneralizedESDTestAD(alpha=0.3)
anomalies = esd_ad.fit_detect(s_train)
plot(s_train, anomaly=anomalies, anomaly_color="red", anomaly_tag="marker")
plt.show()

# ==================================
# 🔹 Persist Anomaly Detection (Positive)
# ==================================
persist_ad = PersistAD(c=3.0, side='positive', window=24)
anomalies = persist_ad.fit_detect(s_train)
plot(s_train, anomaly=anomalies, anomaly_color="red")
plt.show()

# ==================================
# 🔹 Persist Anomaly Detection (Negative)
# ==================================
persist_ad = PersistAD(c=1.5, side='negative', window=24)
anomalies = persist_ad.fit_detect(s_train)
plot(s_train, anomaly=anomalies, anomaly_color="red")
plt.show()

# ==================================
# 🔹 Volatility Shift Anomaly Detection (Yahoo Finance Data)
# ==================================
try:
    s_train = yf.download("TSLA")['Close']
    s_train = validate_series(s_train)

    volatility_shift_ad = VolatilityShiftAD(c=6.0, side='positive', window=30)
    anomalies = volatility_shift_ad.fit_detect(s_train)
    plot(s_train, anomaly=anomalies, anomaly_color='red')
    plt.show()
except Exception as e:
    print(f"Yahoo Finance Data Download Error: {e}")
