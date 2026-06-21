import services.recurring_service as service
from api.responses import safe


def get_recurring_rules(user_id):
    return safe(lambda: service.get_recurring_rules(user_id))


def get_recurring_rule(recurring_rule_id):
    return safe(lambda: service.get_recurring_rule(recurring_rule_id))


def get_due_recurring_rules(as_of=None):
    return safe(lambda: service.get_due_recurring_rules(as_of=as_of))


def create_recurring_rule(account_id, category_id, name, expected_amount,
                          interval, frequency_unit, start_date, next_due_date,
                          end_date=None):
    return safe(lambda: service.create_recurring_rule(
        account_id=account_id,
        category_id=category_id,
        name=name,
        expected_amount=expected_amount,
        interval=interval,
        frequency_unit=frequency_unit,
        start_date=start_date,
        next_due_date=next_due_date,
        end_date=end_date,
    ))


def update_recurring_rule(recurring_rule_id, account_id=None, category_id=None,
                          name=None, expected_amount=None, interval=None,
                          frequency_unit=None, start_date=None, next_due_date=None,
                          end_date=None, status=None):
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
    return safe(lambda: service.update_recurring_rule(recurring_rule_id, **kwargs))


def pause_recurring_rule(recurring_rule_id):
    return safe(lambda: service.pause_recurring_rule(recurring_rule_id))


def resume_recurring_rule(recurring_rule_id):
    return safe(lambda: service.resume_recurring_rule(recurring_rule_id))


def deactivate_recurring_rule(recurring_rule_id):
    return safe(lambda: service.deactivate_recurring_rule(recurring_rule_id))


def generate_transaction(recurring_rule_id):
    return safe(lambda: service.generate_transaction(recurring_rule_id))
