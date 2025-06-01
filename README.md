<<<<<<< HEAD
LSTM (Long Short-Term Memory),LSTM-based Time Series Forecasting Model. air_quality.py
dashboard
train_lstm train forecast
forecast.py
uvicorn main:app --reload
-------------
cd backend :python utils.py
cd backend :python app.py
cd frontend:  python -m http.server 5500 ( click go live)
python -m model.forecast
backend/
│
├── app.py                      # Điểm khởi đầu FastAPI app (chạy server)
│
├── config/                    # Cấu hình chung (env, settings, constants)
│   ├── __init__.py
│   └── config.py              # Biến môi trường, config CORS, DB_URL, etc
│
├── data/                      # Tầng Data (truy xuất dữ liệu, database)
│   ├── __init__.py
│   └── database.py            # Kết nối và xử lý dữ liệu từ CSDL (SQLite/MySQL/PostgreSQL)
│
├── model/                     # AI model, xử lý ML
│   ├── __init__.py
│   ├── forecast.py            # Xử lý model dự báo (LSTM, v.v)
│   ├── predict.py             # Hàm dùng model để dự đoán
│   └── lstm_forecast_multi.ckpt  # File model đã huấn luyện (dạng `.pt`, `.ckpt`, etc.)
│
├── services/                  # Tầng logic xử lý nghiệp vụ
│   ├── __init__.py
│   ├── air_quality.py         # Tính toán AQI, gán mức độ
│   ├── anomaly.py             # Phát hiện bất thường
│   └── utils.py               # Các hàm tiện ích (chuyển đổi đơn vị, logger, etc.)
│
├── controllers/               # Optional: xử lý logic WebSocket, gọi services
│   ├── __init__.py
│   └── websocket_controller.py  # Nếu muốn tách riêng logic WebSocket
│
├── routers/                   # RESTful + WebSocket endpoints
│   ├── __init__.py
│   ├── api_router.py          # Gộp tất cả routes
│   ├── rest/                  # RESTful API
│   │   ├── __init__.py
│   │   └── air_quality_api.py # Các route REST API như `/api/air-quality`
│   └── websocket/             # WebSocket API
│       ├── __init__.py
│       └── data_ws.py         # WebSocket endpoint `/ws/data`, `/ws/air_quality`

nhớ sửa group_id trong predict
=======
# name
PBL_5_KHDLQLDA
>>>>>>> c2fad35fd5418bf2ce9a3d675779d59da754c2fc
