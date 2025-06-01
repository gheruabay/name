from fastapi import APIRouter
from controllers.forecast_controller import generate_forecasts

router = APIRouter()

@router.get("/api/forecast")
def get_forecast():
    result = generate_forecasts()
    return result

if __name__ == "__main__":
    print("Gọi get_forecast():", get_forecast())
