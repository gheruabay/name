import os
import socket
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from routers.api_router import api_router
import uvicorn

app = FastAPI()

# Cho phép CORS toàn bộ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

frontend_path = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/AQI", StaticFiles(directory=frontend_path), name="static")

# / hoặc /index trả về index.html
@app.get("/")
@app.get("/index")
async def index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/{page_name}")
async def dynamic_pages(page_name: str):
    file_path = os.path.join(frontend_path, f"{page_name}.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Trang không tồn tại"}


# Ẩn đuôi .html: /account -> account.html, /air_quality_map -> air_quality_map.html


# Hàm lấy IP LAN
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

async def run():
    ip = get_local_ip()
    print(f"\n✅ Giao diện đang chạy tại: http://{ip}:8000/index\n")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    asyncio.run(run())
