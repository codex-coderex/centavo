import services.recurring_service as service
from api.responses import ok, fail


def get_recurring_rules(user_id):
    try:
        return ok(service.get_recurring_rules(user_id))
    except ValueError as e:
        return fail(e)


def get_recurring_rule(recurring_rule_id):
    try:
        return ok(service.get_recurring_rule(recurring_rule_id))
    except ValueError as e:
        return fail(e)


def get_due_recurring_rules(as_of=None):
    try:
        return ok(service.get_due_recurring_rules(as_of=as_of))
    except ValueError as e:
        return fail(e)


def create_recurring_rule(account_id, category_id, name, expected_amount,
                          interval, frequency_unit, start_date, next_due_date,
                          end_date=None):
    try:
        return ok(
            service.create_recurring_rule(
                account_id=account_id,
                category_id=category_id,
                name=name,
                expected_amount=expected_amount,
                interval=interval,
                frequency_unit=frequency_unit,
                start_date=start_date,
                next_due_date=next_due_date,
                end_date=end_date,
            )
        )
    except ValueError as e:
        return fail(e)


def update_recurring_rule(recurring_rule_id, account_id=None, category_id=None,
                          name=None, expected_amount=None, interval=None,
                          frequency_unit=None, start_date=None, next_due_date=None,
                          end_date=None, status=None):
    try:
        kwargs = {k: v for k, v in {
            "account_id": account_id,
            "category_id": category_id,
            "name": name,
            "expected_amount": expected_amount,
            "interval": interval,
            "frequency_unit": frequency_unit,
            "start_date": start_date,
            "next_due_date": next_due_date,
            "end_date": end_date,
            "status": status,
        }.items() if v is not None}
        return ok(service.update_recurring_rule(recurring_rule_id, **kwargs))
    except ValueError as e:
        return fail(e)


def pause_recurring_rule(recurring_rule_id):
    try:
        return ok(service.pause_recurring_rule(recurring_rule_id))
    except ValueError as e:
        return fail(e)


def resume_recurring_rule(recurring_rule_id):
    try:
        return ok(service.resume_recurring_rule(recurring_rule_id))
    except ValueError as e:
        return fail(e)


def deactivate_recurring_rule(recurring_rule_id):
    try:
        return ok(service.deactivate_recurring_rule(recurring_rule_id))
    except ValueError as e:
        return fail(e)


def generate_transaction(recurring_rule_id):
    try:
        return ok(service.generate_transaction(recurring_rule_id))
    except ValueError as e:
        return fail(e)
