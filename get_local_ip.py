import socket

# Hàm lấy địa chỉ IP trong mạng LAN
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('10.254.254.254', 1))  # Sử dụng một địa chỉ IP bất kỳ trong mạng LAN
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

# In địa chỉ IP LAN ra màn hình
if __name__ == "__main__":
    local_ip = get_local_ip()
    print(f"Địa chỉ IP trong mạng LAN của bạn là: {local_ip}")
