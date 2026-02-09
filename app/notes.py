from app.db import get_conn


def get_note_content(user_id: int) -> str:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT content FROM notes WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    return row["content"] if row else ""


def save_note_content(user_id: int, content: str) -> None:
    # 1 user = 1 note, поэтому делаем UPSERT по PRIMARY KEY (user_id)
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO notes(user_id, content) VALUES(?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET content = excluded.content",
            (user_id, content),
        )