from backend.database import get_db


def get_user_by_username(username):
    return get_db().execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()


def create_user(username, password_hash):
    database = get_db()
    cursor = database.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )
    database.commit()
    return cursor.lastrowid
