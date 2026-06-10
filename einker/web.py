import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, Response, render_template, send_file

from einker.bootstrap import PreflightError, bootstrap
from einker.confparser import get_config
from einker.file_handling import check_cache
from einker.images import daily_images, random_image

logger = logging.getLogger(__name__)

CONFIG = get_config()

BASE_DIR = Path(
    os.environ.get("APP_BASE_DIR", str(Path(__file__).resolve().parents[1]))
)
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "static" / "templates"),
    static_folder=str(BASE_DIR / "static"),
    static_url_path="/static",
)


def get_daily_index(n: int) -> int:
    hour = datetime.now().hour
    return (hour * n) // 24


def current_daily_image(index: int):
    images = daily_images()
    return images[index]


@app.route("/daily")
def daily() -> Response:
    index = get_daily_index(CONFIG.app.images_per_day)
    return send_file(current_daily_image(index), conditional=True)


@app.route("/daily/<int:index>")
def daily_with_index(index):
    index = max(0, min(index, CONFIG.app.images_per_day - 1))
    return send_file(current_daily_image(index), conditional=True)


@app.route("/random")
def random() -> Response:
    image = random_image()
    return send_file(image, conditional=True)


@app.route("/")
@app.route("/daily_view", strict_slashes=False)
def daily_view():
    index = get_daily_index(CONFIG.app.images_per_day)
    image = current_daily_image(index)

    return render_template(
        "daily.html",
        img_src="/daily",
        image_id=image.stem,
    )


@app.route("/daily_view/<int:index>", strict_slashes=False)
def daily_view_with_index(index):
    image = current_daily_image(index)

    return render_template(
        "daily.html",
        img_src="/daily",
        image_id=image.stem,
    )


@app.route("/random_view", strict_slashes=False)
def random_view():
    return render_template("daily.html", img_src="/random")


@app.route("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    try:
        bootstrap()
        check_cache()

    except PreflightError as e:
        logger.error(str(e))
        sys.exit(1)

    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)

    app.run()
