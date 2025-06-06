import pymysql
import pandas as pd
from typing import Optional

# Thông tin kết nối
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "db": "test",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

# -------------------- USERS --------------------

def get_user_by_email(email: str) -> Optional[dict]:
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT name, email, password FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()
            return user if user else None
    finally:
        connection.close()
def get_user_id_by_email(email: str) -> Optional[int]:
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
            return result["id"] if result else None
    finally:
        connection.close()

def create_user(name: str, email: str, password: str):
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, email, password))
        connection.commit()
    finally:
        connection.close()

# -------------------- MEASUREMENTS --------------------

def fetch_data():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM measurements")
            result = cursor.fetchall()
            return pd.DataFrame(result)
    finally:
        connection.close()

def fetch_last_data():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM measurements ORDER BY created_at DESC LIMIT 1")
            result = cursor.fetchall()
            df = pd.DataFrame(result)  # tạo DataFrame từ kết quả
            print("⚡️ Dữ liệu mới nhất trong DB:\n", df)  # In ra terminal
            return pd.DataFrame(result) if result else None
    finally:
        connection.close()

def fetch_last_n_data(group_id=None, n=60):
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            if group_id:
                sql = """
                SELECT * FROM measurements 
                WHERE group_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
                """
                cursor.execute(sql, (group_id, n))
            else:
                sql = "SELECT * FROM measurements ORDER BY created_at DESC LIMIT %s"
                cursor.execute(sql, (n,))
            result = cursor.fetchall()
            return pd.DataFrame(result).sort_values(by="created_at") if result else None
    finally:
        connection.close()
#---------------------HISTORY----------------
def get_user_measurement_history(user_id: int):
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT m.created_at, m.temperature, m.humidity, m.dust, m.mq, m.aqi, m.chat_luong
                FROM user_measurements um
                JOIN measurements m ON um.measurement_id = m.id
                WHERE um.user_id = %s
                ORDER BY m.created_at DESC
            """
            cursor.execute(sql, (user_id,))
            return cursor.fetchall()
    finally:
        connection.close()

