import yfinance as yf
import datetime

# Define start and end dates
start = "2020-01-01"
end = "2025-01-01"

# Fetch General Electric (GE) stock data from Yahoo Finance
ge_data = yf.download("GE", start=start, end=end)

# Save to CSV file
ge_data.to_csv("GE_stock_data.csv")

print("Stock data saved successfully!")
