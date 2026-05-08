import random
from datetime import date
from pathlib import Path

from flask import Flask, send_file

app = Flask(__name__)

IMAGE_DIR = Path("static/images")


def get_daily_image():
    images = list(IMAGE_DIR.glob("*.jpg"))
    seed = date.today().isoformat()
    rng = random.Random(seed)
    return rng.choice(images)


@app.route("/daily")
def daily():
    image = get_daily_image()
    return send_file(image, mimetype="image/jpeg")


if __name__ == "__main__":
    app.run(debug=True)
