from model.predict import generate_forecast

def convert_to_builtin_types(obj):
    if isinstance(obj, dict):
        return {k: convert_to_builtin_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_builtin_types(i) for i in obj]
    elif 'numpy' in str(type(obj)):
        return obj.item()  # chuyển numpy scalar sang Python scalar
    else:
        return obj

def generate_forecasts():
    try:
        print("⚙️ [API] /api/forecast được gọi")
        preds = generate_forecast()
        print("✅ Dự đoán mô hình trả về:", preds)

        safe_preds = convert_to_builtin_types(preds)
        return safe_preds
    except Exception as e:
        print("❌ Forecast error:", e)
        return {"error": str(e)}


