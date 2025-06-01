import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import plotly.graph_objs as go
import plotly.offline as pyo
import os
import time
import webbrowser
from backend.services.air_quality import generate_air_quality_map
from backend.model.forecast import generate_forecast
from database import fetch_data  # Lấy từ MySQL

webbrowser.open('file://' + os.path.realpath("dashboard.html"))

def danh_gia_chat_luong(mq_value, dust_value):
    if mq_value < 450:
        status_mq = "Tốt"
    elif mq_value < 1000:
        status_mq = "Ổn"
    elif mq_value < 1500:
        status_mq = "Không ổn"
    else:
        status_mq = "Nghiêm trọng"

    if dust_value < 35:
        status_dust = "Tốt"
    elif dust_value < 75:
        status_dust = "Ổn"
    elif dust_value < 150:
        status_dust = "Không ổn"
    else:
        status_dust = "Nghiêm trọng"

    issues = []
    if status_mq in ("Không ổn", "Nghiêm trọng"):
        issues.append(f"ở chỉ số mq(khí): {status_mq}")
    if status_dust in ("Không ổn", "Nghiêm trọng"):
        issues.append(f"ở chỉ số bụi mịn: {status_dust}")

    if issues:
        return " ; ".join(issues)
    else:
        return "Tốt" if (status_mq == "Tốt" and status_dust == "Tốt") else "Ổn"

def detect_anomalies(df):
    model = IsolationForest(contamination=0.1, random_state=42)
    features = df[["mq", "dust"]]
    df["anomaly"] = model.fit_predict(features)
    return df

def generate_html(df):
    df = detect_anomalies(df)
    generate_forecast()
    generate_air_quality_map()

    fig = go.Figure()
    normal_data = df[df["anomaly"] == 1]
    anomalies = df[df["anomaly"] == -1]

    for metric, color in zip(["mq", "dust"], ["green", "orange"]):
        fig.add_trace(go.Scatter(
            x=normal_data["created_at"],
            y=normal_data[metric],
            mode='lines+markers',
            name=f'{metric} (Bình thường)',
            line=dict(color=color)
        ))

        symbol = "circle" if metric == "mq" else "x"

        fig.add_trace(go.Scatter(
            x=anomalies["created_at"],
            y=anomalies[metric],
            mode='markers',
            name=f'{metric} (Bất thường)',
            marker=dict(color='red', size=8, symbol=symbol)
        ))

    fig.update_layout(
        title="Chỉ Số MQ & Bụi - Bình Thường & Bất Thường",
        xaxis_title="Thời gian",
        yaxis_title="Giá trị",
        xaxis=dict(tickangle=-45),
        height=600
    )

    latest = df.iloc[-1]
    chat_luong = danh_gia_chat_luong(latest["mq"], latest["dust"])
    table_html = f"""
    <h2>Dữ liệu mới nhất</h2>
    <ul>
        <li>⏱ Vào lúc: {latest['created_at']}</li>
        <li>🌡 Nhiệt độ: {latest['temperature']:.1f} °C</li>
        <li>💧 Độ ẩm: {latest['humidity']:.1f} %</li>
        <li>🧪 MQ (CO2,..): {latest['mq']:.1f} ppm</li>
        <li>🌫 Bụi: {latest['dust']:.1f} µg/m³</li>
        <li>🟡 Chất lượng không khí: <strong>{chat_luong}</strong></li>
    </ul>
    <iframe src="forecast.html" width="100%" height="250" frameborder="0"></iframe>
    """

    chart_html = pyo.plot(fig, include_plotlyjs=False, output_type='div')

    full_html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="5">
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <title>Dashboard Quan Trắc</title>
    </head>
    <body>
        {table_html}
        {chart_html}
        <h2>Tình trạng KK khu vực lân cận</h2>
        <div style="position: relative; width: 100%; height: 400px;">
            <iframe src="air_quality_map.html" width="100%" height="400" frameborder="0"></iframe>
            <a href="air_quality_map.html" target="_blank"
               style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                      z-index: 10; background: transparent;"></a>
        </div>
    </body>
    </html>
    """
    with open("dashboard.html", "w", encoding="utf-8") as f:
        f.write(full_html)

# -------------------- VÒNG LẶP CẬP NHẬT --------------------
if __name__ == "__main__":
    while True:
        df = fetch_data()
        generate_html(df)
        print("Đã cập nhật dashboard.html")
        time.sleep(5)
