from pathlib import Path

from flask import Flask, send_from_directory

import config
from file_handling import check_cache, generate_etag, invalidate_cache
from images import get_daily_image, get_random_image

app = Flask(__name__)


@app.route("/daily")
def daily():
    image = get_daily_image()
    etag = generate_etag(image)
    return send_from_directory(
        config.IMAGE_DIR, image.name, conditional=True, etag=etag
    )


@app.route("/random")
def random_image():
    image = get_random_image()
    etag = generate_etag(image)
    return send_from_directory(
        config.IMAGE_DIR, image.name, conditional=True, etag=etag
    )


@app.route("/debug/list")
def list_images():
    images = list(config.IMAGE_DIR.glob("*.jpg"))
    return {
        "count": len(images),
        "images": [p.name for p in images],
    }


@app.route("/debug/random")
def random_image_without_cache():
    invalidate_cache()
    image = get_random_image()
    return send_from_directory(config.IMAGE_DIR, image.name)


if __name__ == "__main__":
    check_cache()
    app.run()
