from pathlib import Path

from flask import Flask, send_from_directory, Response

import config
from file_handling import check_cache, invalidate_cache, send_image
from images import get_daily_image, get_random_image

app = Flask(__name__)


@app.route("/daily")
def daily() -> Response:
    image = get_daily_image()
    return send_image(image)


@app.route("/random")
def random_image() -> Response:
    image = get_random_image()
    return send_image(image)


@app.route("/debug/list")
def list_images() -> Response:
    images = list(config.IMAGE_DIR.glob("*.jpg"))
    return {
        "count": len(images),
        "images": [p.name for p in images],
    }


@app.route("/debug/random")
def random_image_without_cache() -> Response:
    invalidate_cache()
    image = get_random_image()
    return send_from_directory(config.IMAGE_DIR, image.name)


if __name__ == "__main__":
    check_cache()
    app.run()
