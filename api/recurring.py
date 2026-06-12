import services.recurring_service as service


def get_recurring(user_id):
    return service.get_recurring(user_id)


def get_recurring_by_id(recurring_id):
    return service.get_recurring_by_id(recurring_id)


def get_due_recurring():
    return service.get_due_recurring()


def create_recurring(account_id, amount, interval, frequency_unit, next_due,
                     category_id=None, merchant=None, end_date=None):
    try:
        return service.create_recurring(
            account_id=account_id,
            amount=amount,
            interval=interval,
            frequency_unit=frequency_unit,
            next_due=next_due,
            category_id=category_id,
            merchant=merchant,
            end_date=end_date,
        )
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def update_recurring(recurring_id, amount=None, interval=None, frequency_unit=None,
                     next_due=None, merchant=None, end_date=None,
                     category_id=None, status=None):
    try:
        kwargs = {k: v for k, v in {
            "amount": amount,
            "interval": interval,
            "frequency_unit": frequency_unit,
            "next_due": next_due,
            "merchant": merchant,
            "end_date": end_date,
            "category_id": category_id,
            "status": status,
        }.items() if v is not None}
        service.update_recurring(recurring_id, **kwargs)
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def generate_transaction(recurring_id):
    try:
        return service.generate_transaction(recurring_id)
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def pause_recurring(recurring_id):
    try:
        service.pause_recurring(recurring_id)
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def resume_recurring(recurring_id):
    try:
        service.resume_recurring(recurring_id)
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}


def deactivate_recurring(recurring_id):
    try:
        service.deactivate_recurring(recurring_id)
        return {"ok": True}
    except ValueError as e:
        return {"ok": False, "error": str(e)}
