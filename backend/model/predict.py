import pandas as pd
import numpy as np
import torch
import pytorch_lightning as pl
from torch import nn
from sklearn.preprocessing import StandardScaler
from datetime import timedelta

from data.database import fetch_last_n_data, fetch_last_data
from config.config import TIME_COLUMN
from services.utils import calculate_aqi_pm25, danh_gia_chat_luong

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class LitLSTM(pl.LightningModule):
    def __init__(self, input_size=8, hidden_size=64, num_layers=1, output_size=4 * 10):
        super().__init__()
        self.save_hyperparameters()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.linear = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]
        return self.linear(out)

def prepare_input(df, feature_cols, scaler_x, seq_len=60):
    df = df.sort_values(by=TIME_COLUMN).tail(seq_len).copy()
    df['hour'] = pd.to_datetime(df[TIME_COLUMN]).dt.hour
    df['minute'] = pd.to_datetime(df[TIME_COLUMN]).dt.minute
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['minute_sin'] = np.sin(2 * np.pi * df['minute'] / 60)
    df['minute_cos'] = np.cos(2 * np.pi * df['minute'] / 60)
    x_vals = df[feature_cols]
    x_scaled = scaler_x.transform(x_vals)
    x_tensor = torch.from_numpy(x_scaled.astype(np.float32)).unsqueeze(0).to(DEVICE)
    return x_tensor

def predict_future(model, input_tensor, scaler_y, num_features=4, pred_len=10):
    model.eval()
    with torch.no_grad():
        out = model(input_tensor)
        out = out.view(1, pred_len, num_features)
        y_pred = scaler_y.inverse_transform(out.squeeze(0).cpu().numpy())
    return y_pred

def generate_forecast(group_id="hoa_vang", pred_len=10):
    df = fetch_last_n_data(group_id=group_id, n=60)
    feature_cols = ["temperature", "humidity", "mq", "dust",
                    "hour_sin", "hour_cos", "minute_sin", "minute_cos"]
    num_features = 4

    scaler_x = StandardScaler()
    scaler_y = StandardScaler()
    df['hour'] = pd.to_datetime(df[TIME_COLUMN]).dt.hour
    df['minute'] = pd.to_datetime(df[TIME_COLUMN]).dt.minute
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['minute_sin'] = np.sin(2 * np.pi * df['minute'] / 60)
    df['minute_cos'] = np.cos(2 * np.pi * df['minute'] / 60)
    scaler_x.fit(df[feature_cols])
    scaler_y.fit(df[["temperature", "humidity", "mq", "dust"]])

    input_tensor = prepare_input(df, feature_cols, scaler_x)

    last_df = fetch_last_data()
    if last_df is None or last_df.empty:
        return {"error": "Không có dữ liệu để dự đoán"}

    last_time = pd.to_datetime(last_df.iloc[0]['created_at'])

    ckpt = torch.load("model/lstm_forecast_multi.ckpt", map_location=DEVICE,weights_only=False)
    model = LitLSTM(input_size=8, hidden_size=64, output_size=4 * pred_len)
    model.load_state_dict(ckpt['model_state_dict'])
    model = model.to(DEVICE)
    model.eval()

    preds = predict_future(model, input_tensor, scaler_y, num_features=4, pred_len=pred_len)

    results = []
    for i, row in enumerate(preds, 1):
        # Thay đổi: mỗi bước dự báo nhảy 10 phút
        predict_time = last_time + timedelta(minutes=i * 10)
        temperature, humidity, mq, dust = row
        pm25 = dust / 2
        aqi = calculate_aqi_pm25(pm25)
        chat_luong = danh_gia_chat_luong(mq, pm25)
        results.append({
            "step": i,
            "timestamp": predict_time.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            "mq": round(mq, 2),
            "dust": round(dust, 2),
            "aqi": aqi,
            "chat_luong": chat_luong
        })

    return {"forecast": results}
