import random
import pandas as pd
from datetime import datetime, timedelta
import pymysql

districts = [
    "hai_chau", "thanh_khe", "son_tra", "ngu_hanh_son",
    "lien_chieu", "cam_le", "hoa_vang"
]

# Tính AQI từ PM2.5 (dust) theo chuẩn US EPA
def calculate_aqi_pm25(pm25):
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
    ]

    for bp_low, bp_high, aqi_low, aqi_high in breakpoints:
        if bp_low <= pm25 <= bp_high:
            aqi = ((aqi_high - aqi_low) / (bp_high - bp_low)) * (pm25 - bp_low) + aqi_low
            return round(aqi)
    return 500  # Giá trị vượt giới hạn, cực kỳ nguy hiểm

# Đánh giá chất lượng không khí từ AQI
def evaluate_air_quality(aqi):
    if aqi <= 50:
        return "Tốt"
    elif aqi <= 100:
        return "Trung bình"
    elif aqi <= 150:
        return "Kém"
    else:
        return "Nguy hiểm"

# Sinh dữ liệu mô phỏng
def generate_mock_data(start_time, total_records, group_ids):
    data = []
    current_time = start_time

    for i in range(total_records):
        group_id = random.choice(group_ids)
        temperature = round(random.uniform(31.3, 31.5), 2)
        humidity = round(random.uniform(71.7, 71.9), 2)
        mq = random.randint(1120, 1160)
        dust = round(random.uniform(9.0, 25.0), 2)



        aqi = calculate_aqi_pm25(dust)
        chat_luong = evaluate_air_quality(aqi)

        data.append({
            "created_at": current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "temperature": temperature,
            "humidity": humidity,
            "mq": mq,
            "dust": dust,
            "aqi": aqi,
            "chat_luong": chat_luong,
            "group_id": group_id
        })

        current_time += timedelta(seconds=0.2)

    return pd.DataFrame(data)

# Ghi dữ liệu vào MySQL
def insert_to_mysql(df):
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='test',  # Thay nếu bạn dùng CSDL khác
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            for _, row in df.iterrows():
                sql = """
                INSERT INTO measurements 
                (created_at, temperature, humidity, mq, dust, aqi, chat_luong, group_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    row['created_at'], row['temperature'], row['humidity'],
                    row['mq'], row['dust'], row['aqi'], row['chat_luong'], row['group_id']
                ))
        connection.commit()
    finally:
        connection.close()

# Chạy chương trình
start_datetime = datetime.strptime("2025-05-18 11:00:00", "%Y-%m-%d %H:%M:%S")
df_mock = generate_mock_data(start_datetime, 999, districts)

# Thêm chỉ số index cho group_id nếu cần thiết
district_mapping = {district: idx for idx, district in enumerate(districts)}
df_mock['group_id_index'] = df_mock['group_id'].map(district_mapping)

# Ghi vào CSDL
insert_to_mysql(df_mock)
print("✅ Đã thêm 1000 bản ghi mô phỏng vào MySQL.")
