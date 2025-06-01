import pandas as pd
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# LSTM Model (giống forecast.py)
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2, output_size=4):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]
        out = self.fc(out)
        return out

# Load dữ liệu
df = pd.read_csv("mock_data.csv")
df["created_at"] = pd.to_datetime(df["created_at"])
features = ["mq", "dust", "temperature", "humidity"]
scaler = MinMaxScaler().fit(df[features].values)
data_scaled = scaler.transform(df[features].values)

# Tạo tập huấn luyện (30 bước → dự báo bước 31)
X = []
y = []
T_past = 30
for i in range(len(data_scaled) - T_past):
    X.append(data_scaled[i:i+T_past])
    y.append(data_scaled[i+T_past])

X = np.array(X)
y = np.array(y)

X_tensor = torch.tensor(X, dtype=torch.float32)
y_tensor = torch.tensor(y, dtype=torch.float32)

# Khởi tạo và huấn luyện model
model = LSTMModel(input_size=len(features))
loss_fn = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

print("🔁 Training LSTM...")
for epoch in range(20):
    model.train()
    optimizer.zero_grad()
    output = model(X_tensor)
    loss = loss_fn(output, y_tensor)
    loss.backward()
    optimizer.step()
    print(f"Epoch {epoch+1}/20 - Loss: {loss.item():.6f}")

# Lưu model
torch.save(model.state_dict(), "lstm_model.pt")
print("✅ Đã lưu mô hình vào lstm_model.pt")
