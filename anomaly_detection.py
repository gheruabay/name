import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest


df = pd.read_csv("mock_data.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])


features = df[["co2", "no2", "pm2.5", "pm10"]]

#  Isolation Forest
model = IsolationForest(contamination=0.1, random_state=42)
df["anomaly"] = model.fit_predict(features)

#  điểm bất thường
anomalies = df[df["anomaly"] == -1]
print("\n Dữ liệu bất thường:")
print(anomalies[["timestamp", "co2", "no2", "pm2.5", "pm10"]])
