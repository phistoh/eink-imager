import random
import sqlite3
import uuid
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data/metadata.db"
SCHEMA_VERSION = 1


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    schema = Path(f"schema_v{SCHEMA_VERSION}.sql")
    if not schema.is_file():
        raise FileNotFoundError(f"SQL file missing or invalid: {schema}")

    with get_connection() as conn:
        conn.executescript(
            open(f"schema_v{SCHEMA_VERSION}.sql", encoding="UTF-8").read()
        )


def add_image(image_id, original_name, processed_name, created_at) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO images (
                id,
                original_name,
                processed_name,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """,
            (
                image_id,
                original_name,
                processed_name,
                created_at,
            ),
        )


def set_daily_image(image_id: str, day: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO daily_state (
                date,
                image_id
            )
            VALUES (?, ?)
        """,
            (
                day,
                image_id,
            ),
        )

        conn.execute(
            """
            INSERT OR IGNORE INTO displays (
                image_id,
                display_date
            )
            VALUES (?, ?)
        """,
            (
                image_id,
                day,
            ),
        )


def get_daily_image(day: str) -> str | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT image_id
            FROM daily_state
            WHERE date = ?
        """,
            (day,),
        ).fetchone()

    if row is None:
        return None

    return row["image_id"]


def get_todays_image() -> str | None:
    return get_daily_image(date.today().isoformat())


def get_display_count(image_id: str) -> int:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*) AS count
            FROM displays
            WHERE image_id = ?
        """,
            (image_id,),
        ).fetchone()

    return row["count"] or 0


if __name__ == "__main__":
    # init
    init_db()

    # init testing
    images = ["abc.jpg", "test.jpg", "asdf.jpg", "x.jpg", "yoooo.jpg", "aa.jpg"]
    images_processed = []
    rnd = random.Random()

    # process
    today = date.today().isoformat()
    for img in images:
        rnd.seed(img)
        new_file_name = uuid.UUID(int=rnd.getrandbits(128), version=4).hex
        add_image(new_file_name, img, f"{new_file_name}.jpg", today)
        images_processed.append(new_file_name)

    # change daily image
    for day in range(1, 31):
        today = f"2026-05-{day:02}"
        rnd.seed(today)
        img = rnd.choice(images_processed)
        if get_daily_image(today) is None:
            set_daily_image(img, today)

        print(f"{get_todays_image()}.jpg")
        for img in images_processed:
            print(get_display_count(img))
