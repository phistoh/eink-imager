import logging
import math
import random
from datetime import date
from pathlib import Path

from app.confparser import CONFIG
from app.file_handling import get_image_path_by_id, get_image_paths
from app.metadata import (
    get_daily_image,
    get_display_count,
    get_last_display_date,
    set_daily_image,
)

logger = logging.getLogger(__name__)


def daily_image() -> Path:
    today = date.today()

    image_id = get_daily_image(today.isoformat())
    if image_id:
        path = get_image_path_by_id(image_id)
        if not path.exists():
            logger.error("Missing image file for id=%s", image_id)
            return CONFIG.images.default_image
        return path

    images = get_image_paths()
    if not images:
        return CONFIG.images.default_image
    chosen = choose_image(images, today)
    set_daily_image(chosen.stem, today.isoformat())

    return chosen


def compute_weight(img: Path, today: date) -> float:
    image_id = img.stem

    display_count = get_display_count(image_id)
    weight = 1 / math.sqrt(display_count + 1)

    last_date_str = get_last_display_date(image_id)
    if last_date_str:
        last_date = date.fromisoformat(last_date_str)
        days_since = (today - last_date).days

        if days_since < 7:
            weight *= 0.1
        elif days_since < 30:
            weight *= 0.5

    return weight


def choose_image(images, today: date) -> Path:
    rng = random.Random(today.isoformat())
    weights = []

    for img in images:
        weights.append(compute_weight(img, today))

    return rng.choices(images, weights=weights, k=1)[0]


def random_image() -> Path:
    images = get_image_paths()
    return random.choice(images)
