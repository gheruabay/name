import asyncio
from bleak import BleakClient, BleakScanner
import pymysql

# Kết nối MySQL 
db = pymysql.connect(
    host="localhost",
    user="root",       
    password="",       
    database="test"
)
cursor = db.cursor()

buffer = ""

import asyncio
from bleak import BleakClient, BleakScanner
import pymysql

# Kết nối MySQL 
db = pymysql.connect(
    host="localhost",
    user="root",       
    password="",       
    database="test"
)
cursor = db.cursor()

buffer = ""

def notification_handler(sender, data):
    global buffer
    chunk = data.decode("utf-8", errors="replace")
    buffer += chunk

    while "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        line = line.strip()
        print(f"Raw data: {line}")

        temperature = 0.0
        humidity = 0.0
        mq = 0
        dust = 0.0

        try:
            parts = line.split(",")
            for p in parts:
                kv = p.split("=")
                key = kv[0].strip()
                val = kv[1].strip()

                if key == "T":
                    temperature = float(val)
                elif key == "H":
                    humidity = float(val)
                elif key == "MQ":
                    mq = int(val)
                elif key == "Dust":
                    dust = float(val)

            # In kèm đơn vị ra console
            print(f"Nhiệt độ: {temperature:.2f} °C | Độ ẩm: {humidity:.2f} % | MQ: {mq} ppm | Bụi: {dust:.2f} mg/m³")

            # Chèn vào bảng measurements
            sql = """
                INSERT INTO measurements (temperature, humidity, mq, dust)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (temperature, humidity, mq, dust))
            db.commit()

            print("Đã lưu vào MySQL!")
        except Exception as e:
            print("Lưu data thất baị!:", e)


# Nordic UART Service (NUS)
UART_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"

UART_INDICATE_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"

async def main():
    print("🔍 Đang quét thiết bị BLE...")
    devices = await BleakScanner.discover()
    microbit_address = None

    for d in devices:
        if d.name and "micro:bit" in d.name.lower():
            microbit_address = d.address
            print(f"✅ Tìm thấy micro:bit tại {microbit_address}")
            break

    if not microbit_address:
        print("❌ Không tìm thấy micro:bit qua BLE.")
        return

    async with BleakClient(microbit_address) as client:
        print("🔗 Đã kết nối BLE với micro:bit!")

        services = client.services
        nus_service = next((s for s in services if s.uuid == UART_SERVICE_UUID), None)
        if not nus_service:
            print("⚠️ Micro:bit không có dịch vụ UART.")
            return

        indicate_char = next((c for c in nus_service.characteristics if c.uuid == UART_INDICATE_CHAR_UUID), None)
        if not indicate_char:
            print("⚠️ Không tìm thấy characteristic có Indicate.")
            return

        await client.start_notify(indicate_char.uuid, notification_handler)
        print("📡 Đang nhận dữ liệu qua Indicate... (Nhấn Ctrl+C để dừng)")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️ Dừng nhận dữ liệu.")
        finally:
            await client.stop_notify(indicate_char.uuid)
            cursor.close()
            db.close()

if __name__ == "__main__":
    asyncio.run(main())


# Nordic UART Service (NUS)
UART_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"

UART_INDICATE_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"

async def main():
    print("🔍 Đang quét thiết bị BLE...")
    devices = await BleakScanner.discover()
    microbit_address = None

    for d in devices:
        if d.name and "micro:bit" in d.name.lower():
            microbit_address = d.address
            print(f"✅ Tìm thấy micro:bit tại {microbit_address}")
            break

    if not microbit_address:
        print("❌ Không tìm thấy micro:bit qua BLE.")
        return

    async with BleakClient(microbit_address) as client:
        print("🔗 Đã kết nối BLE với micro:bit!")

        services = client.services
        nus_service = next((s for s in services if s.uuid == UART_SERVICE_UUID), None)
        if not nus_service:
            print("⚠️ Micro:bit không có dịch vụ UART.")
            return

        indicate_char = next((c for c in nus_service.characteristics if c.uuid == UART_INDICATE_CHAR_UUID), None)
        if not indicate_char:
            print("⚠️ Không tìm thấy characteristic có Indicate.")
            return

        await client.start_notify(indicate_char.uuid, notification_handler)
        print("📡 Đang nhận dữ liệu qua Indicate... (Nhấn Ctrl+C để dừng)")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️ Dừng nhận dữ liệu.")
        finally:
            await client.stop_notify(indicate_char.uuid)
            cursor.close()
            db.close()

if __name__ == "__main__":
    asyncio.run(main())
