import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path

from flask import send_from_directory

from einker.confparser import get_config
from einker.metadata import get_all_processed_names

logger = logging.getLogger(__name__)

_cached_image_list = None
_cache_time = None

CONFIG = get_config()


def invalidate_cache() -> None:
    global _cached_image_list, _cache_time

    _cached_image_list = None
    _cache_time = None


def check_cache() -> list[Path]:
    global _cached_image_list, _cache_time

    now = datetime.now()
    if _cached_image_list is None or (now - _cache_time) > timedelta(
        CONFIG.app.cache_ttl
    ):
        _cached_image_list = [
            path
            for path in CONFIG.paths.image_dir.glob("*.jpg")
            if path != CONFIG.images.default_image
        ]
        _cache_time = now

    return _cached_image_list


def generate_etag(image: Path) -> str:
    stat = image.stat()
    raw = f"{image.name}-{stat.st_mtime}-{stat.st_size}"
    return hashlib.md5(raw.encode()).hexdigest()


def get_image_paths() -> list[Path]:
    images = check_cache()
    return images


def get_image_path_by_id(image_id) -> Path:
    return CONFIG.paths.image_dir / image_id / ".jpg"


def send_image(image: Path):
    etag = generate_etag(image)
    return send_from_directory(image.parent, image.name, conditional=True, etag=etag)


def scan_image_consistency() -> bool:
    db_is_consistent = True

    db_files = get_all_processed_names()

    disk_files = {
        path.name for path in CONFIG.paths.image_dir.glob("*.jpg") if path.is_file()
    }

    missing_in_db = disk_files - db_files
    missing_on_disk = db_files - disk_files

    if len(missing_in_db) > 0:
        db_is_consistent = False
        missing_entries = "\n".join(f"- {item}" for item in sorted(missing_in_db))
        logger.warning("Files missing in DB:\n%s", missing_entries)

    if len(missing_on_disk) > 0:
        db_is_consistent = False
        missing_files = "\n".join(f"- {item}" for item in sorted(missing_on_disk))
        logger.warning("DB entries missing on disk:\n%s", missing_files)

    if db_is_consistent:
        logger.info("Database consistency check successful.")

    return db_is_consistent
