ALTER TABLE images ADD COLUMN image_hash TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS idx_images_hash ON images (image_hash);

ALTER TABLE image_features ADD COLUMN edge_density REAL;

ALTER TABLE image_features ADD COLUMN entropy REAL;

PRAGMA user_version = 2;