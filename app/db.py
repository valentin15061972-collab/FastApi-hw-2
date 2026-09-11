ads_database: list = []

users_database: list = []


def get_user_by_username(username: str) -> dict | None:
    for user in users_database:
        if user["name"] == username:
            return user
    return None
