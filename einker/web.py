import logging
import os
from datetime import datetime
from pathlib import Path

from flask import Flask, Response, render_template

from einker.confparser import CONFIG
from einker.file_handling import check_cache, send_image
from einker.images import daily_images, random_image
from einker.metadata import init_db

logger = logging.getLogger(__name__)

BASE_DIR = Path(
    os.environ.get("APP_BASE_DIR", str(Path(__file__).resolve().parents[1]))
)
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


@app.route("/daily/<int:index>")
def daily_with_index(index):
    images = daily_images()
    index = max(0, min(index, CONFIG.app.images_per_day - 1))
    return send_image(images[index])


@app.route("/random")
def random() -> Response:
    image = random_image()
    return send_image(image)


@app.route("/")
@app.route("/daily_view", strict_slashes=False)
def daily_view():
    return render_template("daily.html", img_src="/daily")


@app.route("/daily_view/<int:index>", strict_slashes=False)
def daily_view_with_index(index):
    return render_template("daily.html", img_src=f"/daily/{index}")


@app.route("/random_view", strict_slashes=False)
def random_view():
    return render_template("daily.html", img_src="/random")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    init_db()
    check_cache()
    app.run()
