from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from controllers import account_controller
from datetime import datetime

router = APIRouter()

@router.get("/api/user/info")
def get_user_info(email: str = Header(...)):
    print(f"[DEBUG] Nhận email từ header: {email}")
    try:
        user_data = account_controller.get_user_info_and_history(email)
        print(f"[DEBUG] Dữ liệu user trả về từ controller: {user_data}")

        if not user_data:
            print("[DEBUG] Không tìm thấy user hoặc dữ liệu lịch sử")
            return JSONResponse(status_code=404, content={"error": "Không tìm thấy người dùng hoặc dữ liệu"})

        # ✅ Chuyển datetime thành chuỗi để JSON trả về không lỗi
        for record in user_data["history"]:
            if isinstance(record["created_at"], datetime):
                record["created_at"] = record["created_at"].strftime("%Y-%m-%d %H:%M:%S")

        return JSONResponse(content={
            "name": user_data["name"],
            "email": user_data["email"],
            "history": user_data["history"]
        })

    except Exception as e:
        print(f"[ERROR] Exception khi xử lý API /api/user/info: {e}")
        return JSONResponse(status_code=500, content={"error": f"Lỗi server: {str(e)}"})
