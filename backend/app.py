# app.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.api_router import api_router  # Gồm các router con như forecast, sensor, etc.
import uvicorn
import asyncio

app = FastAPI()

# Cho phép CORS toàn bộ (có thể giới hạn domain cụ thể khi deploy)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hoặc chỉ định domain frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn toàn bộ router chính
app.include_router(api_router)

# Chạy server uvicorn
async def run():
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    asyncio.run(run())
