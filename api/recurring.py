import db.queries.recurring as q


def get_recurring(user_id):
    return q.get_recurring(user_id)


def get_due_recurring():
    return q.get_due_recurring()


def create_recurring(account_id, amount, interval, frequency_unit, next_due,
                     category_id=None, merchant=None, end_date=None):
    recurring_id = q.create_recurring(
        account_id, amount, interval, frequency_unit, next_due,
        category_id=category_id,
        merchant=merchant,
        end_date=end_date,
    )
    return {"recurring_id": recurring_id}


def generate_transaction(recurring_id):
    q.generate_transaction(recurring_id)


def pause_recurring(recurring_id):
    q.pause_recurring(recurring_id)


def resume_recurring(recurring_id):
    q.resume_recurring(recurring_id)
