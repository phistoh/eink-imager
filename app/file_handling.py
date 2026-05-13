import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path

from flask import send_from_directory

from app.confparser import CONFIG

logger = logging.getLogger(__name__)

_cached_image_list = None
_cache_time = None


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
    return images or [CONFIG.images.default_image]


def get_image_path_by_id(id) -> Path:
    return CONFIG.paths.image_dir / id / ".jpg"


def send_image(image: Path):
    etag = generate_etag(image)
    return send_from_directory(
        CONFIG.paths.image_dir, image.name, conditional=True, etag=etag
    )
