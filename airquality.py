import requests
import numpy as np
import math
from map import get_location

API_KEY = "023994f36a7de0dc4d84b4aabb90bd0319969f85"

def evaluate_quality(mq, dust):
    """Đánh giá chất lượng không khí dựa trên MQ và dust"""
    if mq < 450 and dust < 35:
        return "Tốt"
    elif mq < 1000 and dust < 75:
        return "Ổn"
    elif mq < 1500 and dust < 150:
        return "Không ổn"
    return "Nghiêm trọng"

def get_air_quality(lat, lon):
    """Lấy dữ liệu chất lượng không khí từ API"""
    url = f"http://api.waqi.info/feed/geo:{lat};{lon}/?token={API_KEY}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "ok":
                comps = data["data"]["iaqi"]
                pm25 = comps.get("pm25", {}).get("v", 0)
                pm10 = comps.get("pm10", {}).get("v", 0)
                dust = (pm25 + pm10) / 2
                mq = sum(comps.get(k, {}).get("v", 0) for k in ("co", "no2", "so2"))
                return mq, dust
    except:
        pass
    return None, None

def analyze_area():
    """Phân tích chất lượng không khí xung quanh"""
    lat, lon, *_ = get_location()
    radii = [0.3, 0.2, 0.15, 0.1, 0.08, 0.06, 0.04]
    n_points = 20
    angles = np.linspace(0, 2 * np.pi, n_points, endpoint=False)
    
    results = []
    for radius in radii:
        for angle in angles:
            point_lat = lat + radius * math.cos(angle)
            point_lon = lon + radius * math.sin(angle)
            mq, dust = get_air_quality(point_lat, point_lon)
            if mq is not None and dust is not None:
                quality = evaluate_quality(mq, dust)
                results.append({
                    "latitude": point_lat,
                    "longitude": point_lon,
                    "mq": mq,
                    "dust": dust,
                    "quality": quality
                })
    
    # Sắp xếp theo chất lượng
    results.sort(key=lambda x: (x["mq"] + x["dust"]))
    
    # Trả về 5 điểm tốt nhất và xấu nhất
    best = results[:5]
    worst = results[-5:]
    
    return {
        "best_locations": best,
        "worst_locations": worst,
        "center": {"latitude": lat, "longitude": lon}
    }

# Sử dụng
analysis = analyze_area()
print("5 vị trí tốt nhất:")
for loc in analysis["best_locations"]:
    print(f"Lat: {loc['latitude']:.4f}, Lon: {loc['longitude']:.4f} - {loc['quality']}")

print("\n5 vị trí xấu nhất:")
for loc in analysis["worst_locations"]:
    print(f"Lat: {loc['latitude']:.4f}, Lon: {loc['longitude']:.4f} - {loc['quality']}")