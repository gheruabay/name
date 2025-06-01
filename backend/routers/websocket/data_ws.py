from fastapi import APIRouter, WebSocket
from controllers.websocket_controller import handle_data_ws, handle_air_quality_ws

router = APIRouter()

@router.websocket("/ws/data")
async def data_socket(websocket: WebSocket):
    await handle_data_ws(websocket)

@router.websocket("/ws/air_quality")
async def air_quality_socket(websocket: WebSocket):
    await handle_air_quality_ws(websocket)
