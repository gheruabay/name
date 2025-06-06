import jwt
import datetime
import os
from fastapi import HTTPException
from data.database import get_user_by_email, create_user

SECRET_KEY = "secret"
TOKEN_FILE = "token.txt"

def create_token(email: str, expire_minutes: int = 60) -> str:
    payload = {
        "sub": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=expire_minutes)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def save_token_to_file(token: str):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

def load_token_from_file() -> str:
    if not os.path.exists(TOKEN_FILE):
        raise HTTPException(status_code=401, detail="Không tìm thấy token")

    with open(TOKEN_FILE, "r") as f:
        return f.read().strip()

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        logout()
        raise HTTPException(status_code=401, detail="Token đã hết hạn")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")

def logout():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)

def register_user(name: str, email: str, password: str) -> dict:
    if get_user_by_email(email):
        raise HTTPException(status_code=400, detail="Email đã được đăng ký")

    create_user(name, email, password)
    token = create_token(email)
    save_token_to_file(token)
    result = {"token": token, "email": email, "name": name}
    print("Register user result:", result)  # In ra dữ liệu trước khi trả về
    return result

def login_user(email: str, password: str) -> dict:
    user = get_user_by_email(email)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không đúng")

    token = create_token(email)
    save_token_to_file(token)
    result = {"token": token, "email": email, "name": user["name"]}
    print("Login user result:", result)  # In ra dữ liệu trước khi trả về
    return result

