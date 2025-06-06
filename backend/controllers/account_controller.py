from data import database

def get_user_info_and_history(email: str):
    user = database.get_user_by_email(email)
    if not user:
        return None

    user_id = database.get_user_id_by_email(email)
    if not user_id:
        return None

    history = database.get_user_measurement_history(user_id)

    return {
        "name": user["name"],
        "email": user["email"],
        "history": history
    }
