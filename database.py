import pandas as pd
import pymysql

def fetch_data():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',  # Mật khẩu MySQL nếu có thì điền vào đây
        db='test',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM measurements")
            result = cursor.fetchall()
            return pd.DataFrame(result)
    finally:
        connection.close()
        
def fetch_last_data():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',  # Mật khẩu MySQL nếu có thì điền vào đây
        db='test',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            # Lấy bản ghi mới nhất theo trường created_at
            cursor.execute("SELECT * FROM measurements ORDER BY created_at DESC LIMIT 1")
            result = cursor.fetchall()
            
            if result:
                return pd.DataFrame(result)
            else:
                return None  # Trả về None nếu không có dữ liệu
    finally:
        connection.close()

# ✅ Chỉ test khi chạy trực tiếp file database.py
if __name__ == "__main__":
    df = fetch_data()
    print(df.head())
