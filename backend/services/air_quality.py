import requests
import folium
import numpy as np
import math
from map import get_location
from folium.plugins import MarkerCluster
import json

API_KEY = "023994f36a7de0dc4d84b4aabb90bd0319969f85"

def calculate_aqi_pm25(pm25):
    if pm25 <= 50: return 50
    if pm25 <= 100: return 100
    if pm25 <= 200: return 150
    if pm25 <= 250.4: return 200
    if pm25 <= 350.4: return 300
    return 500

def danh_gia_chat_luong(mq, dust):
    aqi = calculate_aqi_pm25(dust)
    if aqi <= 50: return "Tốt"
    elif aqi <= 100: return "Trung bình"
    elif aqi <= 150: return "Kém"
    return "Nguy hiểm"

def get_air_quality(lat, lon,city, region, country):
    url = f"http://api.waqi.info/feed/geo:{lat};{lon}/?token={API_KEY}"
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data.get("status") == "ok":
            comps = data["data"]["iaqi"]
            timestamp = data["data"]["time"]["s"]
            temp = comps.get("t", {}).get("v", None)
            hum = comps.get("h", {}).get("v", None)
            pm25 = comps.get("pm25", {}).get("v", 0)
            pm10 = comps.get("pm10", {}).get("v", 0)
            dust = (pm25 + pm10) / 2
            mq = sum(comps.get(k, {}).get("v", 0) for k in ("co", "no2", "so2"))

            # In ra các giá trị để kiểm tra
            print(f"📍 Tọa độ: ({lat}, {lon})")
            print(f"⏱ Timestamp: {timestamp}")
            print(f"🌡 Nhiệt độ: {temp} °C")
            print(f"💧 Độ ẩm: {hum} %")
            print(f"🧪 MQ (co + no2 + so2): {mq} ppb")
            print(f"🌫 Chỉ số hỗn hợp khí độc: {dust} µg/m³")
            print("-" * 40)

            return timestamp, temp, hum, mq, dust
        else:
            print(f"Không có dữ liệu từ API cho tọa độ ({lat}, {lon})")
    except Exception as e:
        print(f"Lỗi khi gọi API: {e}")

    return None, None, None, None, None

def generate_air_quality_data():
    latitude, longitude, city, region, country = get_location()
    radii = [0.3, 0.2, 0.15, 0.1, 0.08, 0.06, 0.04]
    n_points = 20
    angles = np.linspace(0, 2 * np.pi, n_points, endpoint=False)
    data_points = []

    # Thêm vị trí bản thân
    ts, temp, hum, mq, dust = get_air_quality(latitude, longitude, city, region, country)
    if ts:
        ql = danh_gia_chat_luong(mq, dust)
        popup = (
            f"📍 Vị trí của bạn\n"
            f"⏱ {ts}\n"
            f"🌡 {temp:.1f} °C\n"
            f"💧 {hum:.1f} %\n"
            f"🧪 MQ: {mq:.1f}\n"
            f"🌫 Dust: {dust:.1f} µg/m³\n"
            f"🟢 Chất lượng: {ql}"
        )
        data_points.append({
            "lat": latitude,
            "lon": longitude,
            "city": city,
            "region": region,
            "country": country,
            "quality": ql,
            "popup": popup,
            "timestamp": ts,
            "temperature": temp,
            "humidity": hum,
            "mq": mq,
            "dust": dust
        })

    # Vòng lặp các điểm xung quanh
    for radius in radii:
        coords = [
            (latitude + radius * math.cos(a), longitude + radius * math.sin(a))
            for a in angles
        ]
        for i, (lat, lon) in enumerate(coords):
            ts, temp, hum, mq, dust = get_air_quality(latitude, longitude, city, region, country)
            if ts:
                ql = danh_gia_chat_luong(mq, dust)
                popup = (
                    f"Điểm {i+1}\n"
                    f"⏱ {ts}\n"
                    f"🌡 {temp:.1f} °C\n"
                    f"💧 {hum:.1f} %\n"
                    f"🧪 MQ: {mq:.1f}\n"
                    f"🌫 Dust: {dust:.1f} µg/m³\n"
                    f"🟡 Chất lượng: {ql}"
                )
                data_points.append({
                    "lat": lat,
                    "lon": lon,
                    "city": city,
                    "region": region,
                    "country": country,
                    "quality": ql,
                    "popup": popup,
                    "timestamp": ts,
                    "temperature": temp,
                    "humidity": hum,
                    "mq": mq,
                    "dust": dust
                })
            else:
                data_points.append({
                    "lat": lat,
                    "lon": lon,
                    "city": city,
                    "region": region,
                    "country": country,
                    "quality": "Không rõ",
                    "popup": f"Điểm {i+1}: Không có dữ liệu",
                    "timestamp": None,
                    "temperature": None,
                    "humidity": None,
                    "mq": None,
                    "dust": None
                })
    # ✅ In dữ liệu ra console để kiểm tra
    print("\n===== DỮ LIỆU CHẤT LƯỢNG KHÔNG KHÍ =====")
    for point in data_points:
        print(json.dumps(point, ensure_ascii=False, indent=2))
    print("========================================\n")
    return data_points




def main():
    print("Bắt đầu lấy dữ liệu chất lượng không khí...")
    generate_air_quality_data()
   
    

if __name__ == "__main__":
    main()
