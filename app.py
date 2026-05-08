import random
from pathlib import Path

from flask import Flask, url_for

app = Flask(__name__)

IMAGE_DIR = Path("static/images")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


@app.route("/")
def index():
    images = [
        file.name
        for file in IMAGE_DIR.iterdir()
        if file.suffix.lower() in IMAGE_EXTENSIONS
    ]

    if not images:
        return "<h1>No images found.</h1>"

    image = random.choice(images)

    image_url = url_for("static", filename=f"images/{image}")

    return f"""
    <html>
    <body style="
        margin:0;
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        background:#111;
    ">
        <img
            src="{image_url}"
            style="max-width:95%; max-height:95%;"
        >
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)
