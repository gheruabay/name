import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from data.database import fetch_data
from config.config import TIME_COLUMN, GROUP_COLUMN

# Hyperparameters
SEQ_LEN = 60
PRED_LEN = 10
BATCH_SIZE = 64
EPOCHS = 30
LR = 1e-3
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Biến đầu vào và đầu ra

features = ["temperature", "humidity", "mq", "dust","hour_sin", "hour_cos", "minute_sin", "minute_cos"]
target = ["temperature", "humidity", "mq", "dust"]  # dự đoán tất cả cùng lúc

# 1. Load và xử lý dữ liệu
df = fetch_data()
df[TIME_COLUMN] = pd.to_datetime(df[TIME_COLUMN])
df = df.sort_values(by=[GROUP_COLUMN, TIME_COLUMN])

# Tạo feature thời gian tuần hoàn
df['hour'] = df[TIME_COLUMN].dt.hour
df['minute'] = df[TIME_COLUMN].dt.minute

df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
df['minute_sin'] = np.sin(2 * np.pi * df['minute'] / 60)
df['minute_cos'] = np.cos(2 * np.pi * df['minute'] / 60)

# Chuẩn hóa features và target
scaler_x = StandardScaler()
scaler_y = StandardScaler()


df[features] = scaler_x.fit_transform(df[features])  # chuẩn hóa time features cũng giúp model dễ học

df[target] = scaler_y.fit_transform(df[target])

# 2. Dataset cho chuỗi thời gian
class TimeSeriesDataset(Dataset):
    def __init__(self, data, group_col, features, target, seq_len, pred_len):
        self.data = data
        self.group_col = group_col
        self.features = features
        self.target = target
        self.seq_len = seq_len
        self.pred_len = pred_len

        self.groups = data[group_col].unique()
        self.samples = []

        for g in self.groups:
            df_g = data[data[group_col] == g]
            max_start = len(df_g) - seq_len - pred_len + 1
            for start_idx in range(max_start):
                self.samples.append((g, start_idx))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        g, start_idx = self.samples[idx]
        df_g = self.data[self.data[self.group_col] == g]
        x_seq = df_g[self.features].values[start_idx:start_idx + self.seq_len]
        y_seq = df_g[self.target].values[start_idx + self.seq_len:start_idx + self.seq_len + self.pred_len]
        return torch.tensor(x_seq, dtype=torch.float32), torch.tensor(y_seq, dtype=torch.float32)

# 3. Chia tập train/val
train_df, val_df = train_test_split(df, test_size=0.2, shuffle=False)

train_dataset = TimeSeriesDataset(train_df, GROUP_COLUMN, features, target, SEQ_LEN, PRED_LEN)
val_dataset = TimeSeriesDataset(val_df, GROUP_COLUMN, features, target, SEQ_LEN, PRED_LEN)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

# 4. Model LSTM multi-output
class LSTMForecast(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, num_layers=1, dropout=0.1):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout)
        self.linear = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]  # lấy hidden state cuối cùng
        out = self.linear(out)
        return out

output_size = PRED_LEN * len(target)
model = LSTMForecast(input_size=len(features), hidden_size=64, output_size=output_size).to(DEVICE)

criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LR)

start_epoch = 0
ckpt_path = "model/lstm_forecast_multi.ckpt"

# 5. Load checkpoint nếu có
try:
    checkpoint = torch.load(ckpt_path, map_location=DEVICE)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    start_epoch = checkpoint['epoch']
    print(f"✅ Loaded checkpoint from epoch {start_epoch}")
except FileNotFoundError:
    print("ℹ️ No checkpoint found. Starting from scratch.")

# 6. Training
for epoch in range(start_epoch, EPOCHS):
    model.train()
    train_loss = 0
    for x_batch, y_batch in train_loader:
        x_batch = x_batch.to(DEVICE)
        y_batch = y_batch.to(DEVICE)  # (batch, pred_len, num_targets)

        optimizer.zero_grad()
        output = model(x_batch)  # (batch, pred_len * num_targets)
        output = output.view(-1, PRED_LEN, len(target))  # reshape

        loss = criterion(output, y_batch)
        loss.backward()
        optimizer.step()
        train_loss += loss.item() * x_batch.size(0)
    train_loss /= len(train_loader.dataset)

    # Validation
    model.eval()
    val_loss = 0
    with torch.no_grad():
        for x_batch, y_batch in val_loader:
            x_batch = x_batch.to(DEVICE)
            y_batch = y_batch.to(DEVICE)
            output = model(x_batch).view(-1, PRED_LEN, len(target))
            loss = criterion(output, y_batch)
            val_loss += loss.item() * x_batch.size(0)
        val_loss /= len(val_loader.dataset)

    print(f"Epoch {epoch+1}/{EPOCHS} - Train Loss: {train_loss:.4f} - Val Loss: {val_loss:.4f}")

    # 7. Lưu checkpoint mỗi epoch
    torch.save({
        'epoch': epoch + 1,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'scaler_x': scaler_x,
        'scaler_y': scaler_y,
        'features': features,
        'target': target
    }, ckpt_path)
