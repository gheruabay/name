from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from fastapi.responses import JSONResponse
from controllers.auth_controller import register_user, login_user  # ← dùng đúng đường dẫn

router = APIRouter()

class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

@router.post("/api/auth/register")
def register(user: RegisterSchema):
    token = register_user(user.name, user.email, user.password)
    return JSONResponse(content={"token": token})

@router.post("/api/auth/login")
def login(user: LoginSchema):
    token = login_user(user.email, user.password)
    return JSONResponse(content={"token": token})
