# routers/api_router.py

from fastapi import APIRouter
from routers.websocket import data_ws
from routers.rest import forecast_rest

api_router = APIRouter()

# WebSocket
api_router.include_router(data_ws.router, tags=["WebSocket"])

# RESTful API
api_router.include_router(forecast_rest.router, tags=["Forecast"])
