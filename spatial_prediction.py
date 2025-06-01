import pandas as pd
import numpy as np
from scipy.spatial import cKDTree


df = pd.read_csv("mock_data.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Tạo danh sách tọa độ giả định (tọa độ cảm biến)
locations = np.random.rand(len(df), 2) * 100  # Giả lập tọa độ trong phạm vi 100x100
df["x"], df["y"] = locations[:, 0], locations[:, 1]

# Tọa độ cần dự đoán (giả định)
target_location = np.array([[50, 50]])

# Tạo KDTree để tìm các điểm gần nhất
tree = cKDTree(df[["x", "y"]].values)
distances, indices = tree.query(target_location, k=3)  # Tìm 3 điểm gần nhất

# Chuyển indices về dạng 1D
indices = indices.flatten()
distances = distances.flatten()

# Tính trung bình có trọng số (trọng số nghịch đảo khoảng cách)
weights = 1 / (distances + 1e-5)
predicted_quality = np.average(df["pm2.5"].iloc[indices], weights=weights)

print(f"🔍 Dự đoán PM2.5 tại vị trí {target_location}: {predicted_quality:.2f} µg/m³")
