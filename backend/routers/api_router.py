# routers/api_router.py

from fastapi import APIRouter
from routers.websocket import data_ws
from routers.rest import forecast_rest
from routers.rest import auth_rest
from routers.rest import account_routes
api_router = APIRouter()

# WebSocket
api_router.include_router(data_ws.router, tags=["WebSocket"])

# RESTful API
api_router.include_router(forecast_rest.router, tags=["Forecast"])

api_router.include_router(auth_rest.router, tags=["Auth"])
api_router.include_router(account_routes.router, tags=["Account"])