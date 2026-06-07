import db.queries.users as q


def get_user(user_id):
    return q.get_user(user_id)


def get_all_users():
    return q.get_all_users()


def create_user(name):
    user_id = q.create_user(name)
    return {"user_id": user_id}


def update_user(user_id, name):
    q.update_user(user_id, name=name)
