import services.currency_service as service


def get_currencies():
    return service.get_currencies()


def get_currency(code):
    try:
        return service.get_currency(code)
    except ValueError as e:
        return {"ok": False, "error": str(e)}
