import hashlib
import logging
from datetime import datetime
from pathlib import Path

from flask import send_from_directory

import config

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
    if _cached_image_list is None or (now - _cache_time) > config.CACHE_TTL:
        _cached_image_list = [
            path
            for path in config.IMAGE_DIR.glob("*.jpg")
            if path != config.DEFAULT_IMAGE
        ]
        _cache_time = now

    return _cached_image_list


def generate_etag(image: Path) -> str:
    stat = image.stat()
    raw = f"{image.name}-{stat.st_mtime}-{stat.st_size}"
    return hashlib.md5(raw.encode()).hexdigest()


def get_image_paths() -> list[Path]:
    images = check_cache()
    return images or [config.DEFAULT_IMAGE]


def send_image(image: Path):
    etag = generate_etag(image)
    return send_from_directory(
        config.IMAGE_DIR, image.name, conditional=True, etag=etag
    )
