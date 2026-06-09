ALTER TABLE images
ADD COLUMN eink_status TEXT;

ALTER TABLE images
ADD COLUMN eink_score REAL;

ALTER TABLE images
ADD COLUMN eink_reason TEXT;

CREATE INDEX IF NOT EXISTS idx_images_eink_status
ON images(eink_status);