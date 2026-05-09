import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "blog.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            tags TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    # Seed default admin if no users exist
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if user_count == 0:
        import hashlib
        default_hash = hashlib.sha256("admin123".encode()).hexdigest()
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            ("admin", default_hash),
        )
        conn.commit()
    # Seed sample posts if empty
    count = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    if count == 0:
        seed = [
            ("Hello World", "Welcome to my personal blog! This is my first post. I'm excited to share my thoughts and experiences here.\n\nFeel free to explore and leave comments.", '["intro","blog"]', "2026-05-01 10:00:00"),
            ("Learning FastAPI", "FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints.\n\nKey features:\n- Fast to run\n- Fast to code\n- Fewer bugs\n- Great editor support", '["python","fastapi","tech"]', "2026-05-05 14:30:00"),
            ("Vue 3 Composition API", "Vue 3 introduced the Composition API, which provides a more flexible way to organize component logic.\n\nBenefits:\n- Better code organization\n- Reusable logic with composables\n- Full TypeScript support", '["vue","frontend","tech"]', "2026-05-08 09:15:00"),
        ]
        conn.executemany(
            "INSERT INTO posts (title, content, tags, created_at) VALUES (?, ?, ?, ?)",
            seed,
        )
        conn.commit()
    conn.close()


def row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["tags"] = json.loads(d["tags"])
    return d


def list_posts(tag: str | None = None, q: str | None = None) -> list[dict]:
    conn = get_conn()
    sql = "SELECT * FROM posts WHERE 1=1"
    params: list = []
    if tag:
        sql += " AND tags LIKE ?"
        params.append(f'%"{tag}"%')
    if q:
        sql += " AND (title LIKE ? OR content LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])
    sql += " ORDER BY id DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [row_to_dict(r) for r in rows]


def get_post(post_id: int) -> dict | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    conn.close()
    return row_to_dict(row) if row else None


def create_post(title: str, content: str, tags: list[str]) -> dict:
    conn = get_conn()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur = conn.execute(
        "INSERT INTO posts (title, content, tags, created_at) VALUES (?, ?, ?, ?)",
        (title, content, json.dumps(tags), now),
    )
    conn.commit()
    post = get_post(cur.lastrowid)
    conn.close()
    return post


def update_post(post_id: int, title: str, content: str, tags: list[str]) -> dict | None:
    conn = get_conn()
    cur = conn.execute(
        "UPDATE posts SET title = ?, content = ?, tags = ? WHERE id = ?",
        (title, content, json.dumps(tags), post_id),
    )
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return get_post(post_id) if updated else None


def delete_post(post_id: int) -> bool:
    conn = get_conn()
    cur = conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted


def list_tags() -> list[str]:
    conn = get_conn()
    rows = conn.execute("SELECT tags FROM posts").fetchall()
    conn.close()
    tags = set()
    for row in rows:
        for t in json.loads(row["tags"]):
            tags.add(t)
    return sorted(tags)


def get_user(username: str) -> dict | None:
    conn = get_conn()
    row = conn.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_password(username: str, new_hash: str) -> bool:
    conn = get_conn()
    cur = conn.execute(
        "UPDATE users SET password_hash = ? WHERE username = ?",
        (new_hash, username),
    )
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated
