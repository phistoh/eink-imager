import hashlib
from datetime import datetime
from pathlib import Path

import config

_cached_image_list = None
_cache_time = None


def invalidate_cache():
    global _cached_image_list, _cache_time

    _cached_image_list = None
    _cache_time = None


def check_cache() -> list:
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


def generate_etag(path: Path) -> str:
    stat = path.stat()
    raw = f"{path.name}-{stat.st_mtime}-{stat.st_size}"
    return hashlib.md5(raw.encode()).hexdigest()


def get_image_paths():
    images = check_cache()
    return images or config.DEFAULT_IMAGE
