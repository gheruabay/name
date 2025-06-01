import pandas as pd
import pymysql

def fetch_data():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',  
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
        password='',  
        db='test',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM measurements ORDER BY created_at DESC LIMIT 1")
            result = cursor.fetchall()
            
            if result:
                return pd.DataFrame(result)
            else:
                return None
    finally:
        connection.close()

def fetch_last_n_data(group_id=None, n=60):
    """
    Lấy n bản ghi mới nhất (theo created_at) từ bảng measurements.
    Nếu group_id được truyền vào, lọc theo group_id đó.
    """
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',  
        db='test',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
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
            if result:
                # Trả về DataFrame theo thứ tự thời gian tăng dần (để dùng chuẩn)
                return pd.DataFrame(result).sort_values(by="created_at")
            else:
                return None
    finally:
        connection.close()

# ✅ Test khi chạy trực tiếp
if __name__ == "__main__":
    df = fetch_data()
    

    df_last_n = fetch_last_n_data(group_id="hoa_vang", n=5)
    print("\n5 bản ghi mới nhất nhóm 'hoa_vang':")
    print(df_last_n)
