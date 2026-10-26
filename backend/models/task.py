from backend.database import get_db


def get_tasks_for_user(user_id):
    return get_db().execute(
        """
        SELECT id, user_id, title, description, status, created_at
        FROM tasks
        WHERE user_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (user_id,),
    ).fetchall()


def get_task_for_user(task_id, user_id):
    return get_db().execute(
        """
        SELECT id, user_id, title, description, status, created_at
        FROM tasks
        WHERE id = ? AND user_id = ?
        """,
        (task_id, user_id),
    ).fetchone()


def create_task(user_id, title, description, status):
    database = get_db()
    cursor = database.execute(
        """
        INSERT INTO tasks (user_id, title, description, status)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, title, description, status),
    )
    database.commit()
    return get_task_for_user(cursor.lastrowid, user_id)


def update_task(task_id, user_id, title, description, status):
    database = get_db()
    database.execute(
        """
        UPDATE tasks
        SET title = ?, description = ?, status = ?
        WHERE id = ? AND user_id = ?
        """,
        (title, description, status, task_id, user_id),
    )
    database.commit()
    return get_task_for_user(task_id, user_id)


def delete_task(task_id, user_id):
    database = get_db()
    cursor = database.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, user_id),
    )
    database.commit()
    return cursor.rowcount > 0
