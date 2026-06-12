import db.queries.users as users_q


def get_users():
    return users_q.get_users()


def get_user(user_id: int):
    return users_q.get_user(user_id)


def create_user(name: str):
    name = name.strip()

    if not name:
        raise ValueError("User name is required")

    user_id = users_q.create_user(name)

    return {"user_id": user_id}


def update_user(user_id: int, name: str):
    name = name.strip()

    if not name:
        raise ValueError("User name cannot be empty")

    if users_q.get_user(user_id) is None:
        raise ValueError("User does not exist")

    users_q.update_user(user_id, name=name)