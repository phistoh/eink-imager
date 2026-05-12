import json
import logging
import math
import random
from datetime import date
from pathlib import Path

from file_handling import get_image_paths

logger = logging.getLogger(__name__)

METADATA_FILE = Path("data/metadata.json")


def choose_image(images):
    weights = [1 / (img["display_count"] + 1) for img in images]

    return random.choices(images, weights=weights, k=1)[0]


# TODO: Store the daily image, so that the displaying of the daily image does not trigger to display another image
def get_daily_image() -> Path:
    images = get_image_paths()
    today = date.today()
    rng = random.Random(today.isoformat())

    metadata = load_metadata()
    image_metadata = metadata.get("images", {})

    weights = []

    for img in images:
        data = image_metadata.get(img.stem, {})
        display_dates = data.get("display_dates", [])
        display_count = len(display_dates)
        weight = 1 / math.sqrt(display_count + 1)
        if display_dates:
            last_date = date.fromisoformat(max(display_dates))
            days_since = (today - last_date).days
            if days_since < 7:
                weight *= 0.1
            elif days_since < 30:
                weight *= 0.5
        weights.append(weight)

    img = rng.choices(images, weights=weights, k=1)[0]
    update_display_count(metadata, str(img.stem))

    return img


def get_random_image() -> Path:
    images = get_image_paths()
    return random.choice(images)


def load_metadata() -> dict:
    if not METADATA_FILE.exists():
        return {"images": {}}

    with open(METADATA_FILE, "r", encoding="UTF-8") as f:
        return json.load(f)


def save_metadata(data: dict) -> None:
    tmp = METADATA_FILE.with_suffix(".tmp")

    with open(tmp, "w", encoding="UTF-8") as f:
        json.dump(data, f, indent=2)

    tmp.replace(METADATA_FILE)


def is_new_image_for_today(metadata: dict) -> bool:
    today = date.today().isoformat()
    if today in metadata["display_dates"]:
        return False

    metadata["display_dates"].append(today)
    return True


def update_display_count(metadata: dict, id: str) -> bool:
    if id not in metadata["images"]:
        metadata["images"][id] = {"display_dates": []}

    if is_new_image_for_today(metadata["images"][id]):
        save_metadata(metadata)
