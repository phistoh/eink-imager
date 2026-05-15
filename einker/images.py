import logging
import math
import random
from datetime import date
from pathlib import Path

from einker.confparser import get_config
from einker.file_handling import get_image_paths
from einker.metadata import get_display_count, get_last_display_date, set_daily_images

logger = logging.getLogger(__name__)

CONFIG = get_config()


def daily_images() -> Path:
    today = date.today()

    images = get_image_paths()
    if not images:
        return [CONFIG.images.default_image] * CONFIG.app.images_per_day

    chosen = choose_images(images, CONFIG.app.images_per_day, today)
    if len(chosen) < CONFIG.app.images_per_day:
        return chosen + [CONFIG.images.default_image] * (
            CONFIG.app.images_per_day - len(chosen)
        )
    set_daily_images([img.stem for img in chosen], today.isoformat())

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


def choose_images(images, n: int, today: date) -> list[Path]:
    rng = random.Random(today.isoformat())
    weights = []

    for img in images:
        weights.append(compute_weight(img, today))

    return rng.sample(images, k=min(n, len(images)))


def random_image() -> Path:
    images = get_image_paths()
    if not images:
        images = CONFIG.images.default_image
    return random.choice(images)
