import hashlib
import random
from datetime import date, datetime, timedelta
from pathlib import Path

from flask import Flask, Response, abort, request, send_from_directory

app = Flask(__name__)

IMAGE_DIR = Path(__file__).parent / Path("static/images")

_cached_image_list = None
_cache_time = None
CACHE_TTL = timedelta(hours=24)
DEFAULT_IMAGE = Path("static/default.jpg")


def invalidate_cache():
    global _cached_image_list, _cache_time

    _cached_image_list = None
    _cache_time = None


def check_cache() -> list:
    global _cached_image_list, _cache_time

    now = datetime.now()
    if _cached_image_list is None or (now - _cache_time) > CACHE_TTL:
        _cached_image_list = list(IMAGE_DIR.glob("*.jpg"))
        _cache_time = now

    return _cached_image_list


def generate_etag(path: Path) -> str:
    stat = path.stat()
    raw = f"{path.name}-{stat.st_mtime}-{stat.st_size}"
    return hashlib.md5(raw.encode()).hexdigest()


def get_images():
    images = check_cache()
    return images or DEFAULT_IMAGE


def get_daily_image():
    images = get_images()
    seed = date.today().isoformat()
    rng = random.Random(seed)
    return rng.choice(images)


def get_random_image():
    images = get_images()
    return random.choice(images)


@app.route("/daily")
def daily():
    image = get_daily_image()
    etag = generate_etag(image)
    return send_from_directory(IMAGE_DIR, image.name, conditional=True, etag=etag)


@app.route("/random")
def random_image():
    image = get_random_image()
    etag = generate_etag(image)
    return send_from_directory(IMAGE_DIR, image.name, conditional=True, etag=etag)


@app.route("/debug/list")
def list_images():
    images = list(IMAGE_DIR.glob("*.jpg"))
    return {
        "count": len(images),
        "images": [p.name for p in images],
    }


@app.route("/debug/random")
def random_image_without_cache():
    invalidate_cache()
    image = get_random_image()
    return send_from_directory(IMAGE_DIR, image.name)


if __name__ == "__main__":
    check_cache()
    app.run()
