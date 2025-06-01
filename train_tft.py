import pytorch_lightning as pl
import torch
import torch.nn as nn
import pandas as pd
from pytorch_forecasting import TemporalFusionTransformer
from pytorch_forecasting.data import TimeSeriesDataSet
from torch.utils.data import DataLoader
from sqlalchemy import create_engine
from datetime import datetime
import torchmetrics  # Đảm bảo đã import torchmetrics

# B1: Đọc dữ liệu từ MySQL
def fetch_data_from_mysql():
    engine = create_engine("mysql+pymysql://root:@localhost/test")
    query = "SELECT * FROM measurements"
    df = pd.read_sql(query, engine)
    return df

# B2: Chuẩn bị dữ liệu cho TFT
def prepare_data(df):
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values('created_at')

    # Tính chỉ số thời gian
    df['time_idx'] = (df['created_at'] - df['created_at'].min()).dt.total_seconds().astype(int)

    # Đặc trưng thời gian
    df['hour'] = df['created_at'].dt.hour
    df['minute'] = df['created_at'].dt.minute
    df['dayofweek'] = df['created_at'].dt.dayofweek

    # Đảm bảo group_id_index là chuỗi (categorical)
    df['group_id_index'] = df['group_id'].astype(str)

    target = "temperature"
    max_encoder_length = 24
    max_prediction_length = 6

    dataset = TimeSeriesDataSet(
        df,
        time_idx="time_idx",
        target=target,
        group_ids=["group_id_index"],
        max_encoder_length=max_encoder_length,
        max_prediction_length=max_prediction_length,
        static_categoricals=["group_id_index"],
        time_varying_known_reals=["hour", "minute", "dayofweek", "humidity", "mq", "dust"],
        time_varying_unknown_reals=[target],
        add_relative_time_idx=True,
        add_target_scales=True,
        add_encoder_length=True,
        allow_missing_timesteps=True
    )

    # Chia dữ liệu thủ công (tạo tập huấn luyện và kiểm tra)
    train_size = int(0.8 * len(df))
    train_df = df[:train_size]
    val_df = df[train_size:]

    train_dataset = TimeSeriesDataSet.from_dataset(dataset, train_df)
    val_dataset = TimeSeriesDataSet.from_dataset(dataset, val_df)

    return train_dataset, val_dataset

# B3: Huấn luyện mô hình
def train_tft(train_dataset, val_dataset):
    train_dataloader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    val_dataloader = DataLoader(val_dataset, batch_size=64)

    # Tạo mô hình TFT mà không cần tham số metrics
    tft = TemporalFusionTransformer.from_dataset(
        train_dataset,
        learning_rate=0.03,
        hidden_size=16,
        attention_head_size=4,
        dropout=0.1,
        hidden_continuous_size=8,
        output_size=1,
        loss=nn.MSELoss(),  # Chỉ cần truyền loss
        log_interval=10,
        reduce_on_plateau_patience=4,
    )

    # Sử dụng PyTorch Lightning để huấn luyện
    trainer = pl.Trainer(max_epochs=20, accelerator="auto", enable_model_summary=True)
    trainer.fit(tft, train_dataloaders=train_dataloader, val_dataloaders=val_dataloader)

    # Lưu mô hình
    model_path = "tft_model.pt"
    torch.save(tft.state_dict(), model_path)
    print(f"✅ Đã lưu mô hình tại {model_path}")

    return tft

# B4: Main
def main():
    df = fetch_data_from_mysql()
    train_dataset, val_dataset = prepare_data(df)
    model = train_tft(train_dataset, val_dataset)
    print("✅ Đã huấn luyện xong mô hình TFT.")

if __name__ == "__main__":
    main()
