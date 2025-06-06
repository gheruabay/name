import json
import asyncio
from fastapi import WebSocket
from data.database import fetch_last_data
from services.air_quality import generate_air_quality_data
from starlette.websockets import WebSocketDisconnect
async def handle_data_ws(websocket: WebSocket):
    print(f"Client {websocket.client} connected (data)")
    await websocket.accept()

    try:
        while True:
            df = fetch_last_data()
            if df is not None and not df.empty:
                latest = df.iloc[0]
                payload = {
                    "time": str(latest["created_at"]),
                    "temperature": float(latest["temperature"]),
                    "humidity": float(latest["humidity"]),
                    "mq": int(latest["mq"]),
                    "dust": float(latest["dust"]),
                    "quality": str(latest["chat_luong"]),
                    "aqi": int(latest["aqi"])
                }
                await websocket.send_text(json.dumps(payload))
            else:
                print("Không có dữ liệu.")
            await asyncio.sleep(1.5)
    except WebSocketDisconnect:
        print(f"Client {websocket.client} disconnected")

async def handle_air_quality_ws(websocket: WebSocket):
    print(f"Client {websocket.client} connected (air_quality)")
    await websocket.accept()

    data_points = generate_air_quality_data()

    if not data_points:
        await websocket.send_text(json.dumps({"error": "Không có dữ liệu"}))
        await websocket.close()
        return

    user_point = data_points[0]

    response = {
        "latitude": user_point["lat"],
        "longitude": user_point["lon"],
        "city": user_point["city"],
        "region": user_point["region"],
        "country": user_point["country"],
        "data_points": data_points
    }

    await websocket.send_text(json.dumps(response, ensure_ascii=False))
    await websocket.close()
