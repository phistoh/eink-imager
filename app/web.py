import logging
from pathlib import Path

from flask import Flask, Response, render_template, send_from_directory

from app.confparser import CONFIG
from app.file_handling import check_cache, invalidate_cache, send_image
from app.images import get_daily_image, get_random_image

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "data" / "templates"),
    static_folder=str(BASE_DIR / "static"),
    static_url_path="/static",
)


@app.route("/daily")
def daily() -> Response:
    image = get_daily_image()
    return send_image(image)


@app.route("/random")
def random_image() -> Response:
    image = get_random_image()
    return send_image(image)


@app.route("/")
@app.route("/daily_view", strict_slashes=False)
def daily_view():
    return render_template("daily.html", img_src="/daily")


@app.route("/random_view", strict_slashes=False)
def random_view():
    return render_template("daily.html", img_src="/random")


if __name__ == "__main__":
    check_cache()
    app.run()
