import requests

def get_location():
    response = requests.get("https://ipinfo.io/json")  
    data = response.json()
    lat, lon = data["loc"].split(",")  # Lấy tọa độ
    return float(lat), float(lon), data["city"], data["region"], data["country"]

latitude, longitude, city, region, country = get_location()
print(f"📍 Bạn đang ở: {city}, {region}, {country} ({latitude}, {longitude})")
