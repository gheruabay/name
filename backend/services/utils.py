import pymysql
from datetime import datetime
from map import get_location
import random
from bleak import BleakScanner, BleakClient
import asyncio

UART_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
UART_INDICATE_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"

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
            return round(((aqi_high - aqi_low) / (bp_high - bp_low)) * (pm25 - bp_low) + aqi_low)
    return 500

def danh_gia_chat_luong(mq, pm25):
    aqi = calculate_aqi_pm25(pm25)
    if aqi <= 50:
        return "Tốt"
    elif aqi <= 100:
        return "Trung bình"
    elif aqi <= 200:
        return "Không ổn"
    return "Nguy hiểm"

async def insert_mock_data_loop():
    print("🔄 Bắt đầu kết nối và ghi dữ liệu BLE vào MySQL...")

    # Tìm địa chỉ micro:bit 1 lần
    microbit_address = None
    while not microbit_address:
        print("🔍 Đang quét thiết bị BLE...")
        devices = await BleakScanner.discover()
        for d in devices:
            if d.name and "micro:bit" in d.name.lower():
                microbit_address = d.address
                break
        if not microbit_address:
            print("❌ Không tìm thấy micro:bit BLE.")
            await asyncio.sleep(2.5)

    print(f"✅ Đã tìm thấy micro:bit tại địa chỉ {microbit_address}")

    async with BleakClient(microbit_address) as client:
        print("🔌 Đang kết nối tới micro:bit...")
        if not client.is_connected:
            await client.connect()
        print("✅ Đã kết nối!")

        # Lấy dịch vụ UART
        services = await client.get_services()
        nus_service = services.get_service(UART_SERVICE_UUID)
        indicate_char = nus_service.get_characteristic(UART_INDICATE_CHAR_UUID)

        if not indicate_char:
            print("❌ Không tìm thấy characteristic phù hợp.")
            return

        buffer = ""
        buffer_lock = asyncio.Lock()

        def handle_notification(sender, data):
            nonlocal buffer
            decoded = data.decode("utf-8", errors="replace")
            asyncio.create_task(update_buffer(buffer_lock, decoded, buffer))

        async def update_buffer(lock, data_chunk, buf):
            async with lock:
                nonlocal buffer
                buffer += data_chunk

        # Bắt đầu nhận notify
        await client.start_notify(indicate_char.uuid, handle_notification)

        while True:
            try:
                await asyncio.sleep(3.5)  # Delay giữa các lần xử lý

                async with buffer_lock:
                    lines = buffer.strip().split("\n")
                    buffer = ""  # reset sau khi xử lý

                last_line = lines[-1] if lines else ""
                print("📦 Dữ liệu thô:", last_line)

                # Tách key-value từ dòng dữ liệu
                parts = last_line.split(",")
                data_dict = {k.strip(): v.strip() for p in parts if "=" in p for k, v in [p.split("=")]}

                temperature = round(float(data_dict.get("T", 0.0)), 2)
                humidity = round(float(data_dict.get("H", 0.0)), 2)
                mq = int(data_dict.get("MQ", 0))
                dust = round(float(data_dict.get("Dust", 0.0)), 2)
                dust += random.uniform(5, 30)
                dust = round(dust, 2)

                aqi = calculate_aqi_pm25(dust)
                chat_luong = danh_gia_chat_luong(mq, dust)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                lat, lon, city, _, _ = get_location()
                group_id = city.lower().replace(" ", "_")
                if temperature == 0.0:
                 print("Bỏ qua.")
                 continue
                print("📊 Phân tích:", temperature, humidity, mq, dust, aqi, chat_luong, city)

                # Ghi vào MySQL
                connection = pymysql.connect(
                    host='localhost', user='root', password='', db='test',
                    charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor
                )
                with connection.cursor() as cursor:
                    sql = """
                    INSERT INTO measurements 
                    (created_at, temperature, humidity, mq, dust, aqi, chat_luong, group_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (
                        timestamp, temperature, humidity, mq, dust, aqi, chat_luong, group_id
                    ))
                connection.commit()
                connection.close()

                print("✅ Đã lưu dữ liệu vào MySQL.")

            except Exception as e:
                print(f"❌ Lỗi khi xử lý vòng lặp: {e}")

def main():
    asyncio.run(insert_mock_data_loop())

if __name__ == "__main__":
    main()
