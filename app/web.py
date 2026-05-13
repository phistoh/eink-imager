import logging
from datetime import datetime
from pathlib import Path

from flask import Flask, Response, render_template

from app.confparser import CONFIG
from app.file_handling import check_cache, send_image
from app.images import daily_images, random_image
from app.metadata import init_db

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "data" / "templates"),
    static_folder=str(BASE_DIR / "static"),
    static_url_path="/static",
)


def get_daily_index(n: int) -> int:
    hour = datetime.now().hour
    return (hour * n) // 24


@app.route("/daily")
def daily() -> Response:
    images = daily_images()
    index = get_daily_index(CONFIG.app.images_per_day)
    return send_image(images[index])


@app.route("/random")
def random() -> Response:
    image = random_image()
    return send_image(image)


@app.route("/")
@app.route("/daily_view", strict_slashes=False)
def daily_view():
    return render_template("daily.html", img_src="/daily")


@app.route("/random_view", strict_slashes=False)
def random_view():
    return render_template("daily.html", img_src="/random")


if __name__ == "__main__":
    init_db()
    check_cache()
    app.run()
