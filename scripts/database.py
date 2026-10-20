import sqlite3
import json
from pathlib import Path


# Store the database inside the project's data folder.
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "content_studio.db"


def get_connection():
    """Create a connection to the local SQLite database."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def init_db():
    """Create the generations table if it doesn't exist."""

    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS generations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                episode_title TEXT NOT NULL,
                genre TEXT,
                platform TEXT,
                audience TEXT,
                tone TEXT,
                episode_details TEXT,
                generated_content TEXT NOT NULL,
                generation_time REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_generation(
    episode_title,
    genre,
    platform,
    audience,
    tone,
    episode_details,
    generated_content,
    generation_time,
):
    """Save one generated result and return its database ID."""

    # Store the generated content as JSON text.
    if isinstance(generated_content, dict):
        generated_content = json.dumps(
            generated_content,
            ensure_ascii=False,
        )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO generations (
                episode_title,
                genre,
                platform,
                audience,
                tone,
                episode_details,
                generated_content,
                generation_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                episode_title,
                genre,
                platform,
                audience,
                tone,
                episode_details,
                generated_content,
                generation_time,
            ),
        )

        return cursor.lastrowid


def get_all_generations():
    """Retrieve saved generations, newest first."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM generations
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()

        return [dict(row) for row in rows]


def get_generation_by_id(generation_id):
    """Retrieve a single generation using its ID."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM generations
            WHERE id = ?
            """,
            (generation_id,),
        ).fetchone()

        return dict(row) if row else None


def delete_generation(generation_id):
    """Delete one saved generation. Return True if deleted."""

    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM generations
            WHERE id = ?
            """,
            (generation_id,),
        )

        return cursor.rowcount > 0
