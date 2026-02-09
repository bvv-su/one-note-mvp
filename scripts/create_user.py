import sys

from app.db import init_db, get_conn
from app.auth import make_password_hash


def main():
    if len(sys.argv) != 3:
        print("Usage: python -m scripts.create_user <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    init_db()
    pw_hash = make_password_hash(password)

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users(username, password_hash) VALUES(?, ?)",
            (username, pw_hash),
        )
        conn.commit()

    print(f"User created: {username}")


if __name__ == "__main__":
    main()