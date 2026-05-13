CREATE TABLE IF NOT EXISTS images (
    id TEXT PRIMARY KEY,
    original_name TEXT NOT NULL,
    processed_name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS displays (
    image_id TEXT NOT NULL,
    display_date TEXT NOT NULL,
    PRIMARY KEY (image_id, display_date),
    FOREIGN KEY (image_id) REFERENCES images(id)
);

CREATE TABLE IF NOT EXISTS daily_state (
    date TEXT PRIMARY KEY,
    image_id TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_displays_image_id
ON displays(image_id);

CREATE INDEX IF NOT EXISTS idx_displays_image_date
ON displays(image_id, display_date);
