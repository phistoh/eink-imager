import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data/metadata.db"
LATEST_SCHEMA_VERSION = 1


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    schema = BASE_DIR / f"static/schemas/schema_v{LATEST_SCHEMA_VERSION}.sql"
    if not schema.is_file():
        raise FileNotFoundError(f"SQL file missing or invalid: {schema}")

    with get_connection() as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(schema.read_text(encoding="UTF-8"))


def get_user_version(conn) -> int:
    return conn.execute("PRAGMA user_version").fetchone()[0]


def migrate_db():
    with get_connection() as conn:
        version = get_user_version(conn)

        while version < LATEST_SCHEMA_VERSION:
            next_version = version + 1

            migration = (
                BASE_DIR
                / "static"
                / "schemas"
                / "migrations"
                / f"v{version}_to_v{next_version}.sql"
            )

            conn.executescript(migration.read_text(encoding="UTF-8"))

            version = next_version


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


def add_image_features(image_id: str, features: dict) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO image_features (
                image_id,
                brightness,
                hue,
                saturation,
                contrast
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                image_id,
                features["brightness"],
                features["hue"],
                features["saturation"],
                features["contrast"],
            ),
        )


def set_daily_images(image_ids: list[str], day: str) -> None:
    with get_connection() as conn:
        for image_id in image_ids:
            conn.execute(
                """
                INSERT OR IGNORE INTO daily_state (date, image_id)
                VALUES (?, ?)
                """,
                (day, image_id),
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


def get_daily_images(day: str) -> str | None:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT image_id
            FROM daily_state
            WHERE date = ?
            """,
            (day,),
        ).fetchall()

    return [r["image_id"] for r in rows]


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


def get_last_display_date(image_id: str) -> str | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT MAX(display_date) AS last_date
            FROM displays
            WHERE image_id = ?
            """,
            (image_id,),
        ).fetchone()

    return row["last_date"]


def get_all_processed_names() -> set[str]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT processed_name
            FROM images
            """
        ).fetchall()

    return {row["processed_name"] for row in rows}


def delete_image(image_id: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            DELETE FROM images
            WHERE id = ?
            """,
            (image_id,),
        )
