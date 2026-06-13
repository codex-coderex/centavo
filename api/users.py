import services.user_service as service


def get_users():
    return service.get_users()


def get_user(user_id):
    return service.get_user(user_id)


def create_user(name, currency_code):
    try:
        return service.create_user(name, currency_code)
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def update_user(user_id, name=None, currency_code=None):
    try:
        service.update_user(user_id, name=name, currency_code=currency_code)
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}
