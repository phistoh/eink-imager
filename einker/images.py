import logging
import math
import random
from datetime import date, datetime
from pathlib import Path

from einker.confparser import get_config
from einker.file_handling import get_image_paths, invalidate_cache
from einker.metadata import (
    get_display_count,
    get_image_features,
    get_last_display_date,
    set_daily_images,
)
from einker.utils import lerp

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


def cooldown_modifier(image_id: str, today: date) -> float:
    last_date_str = get_last_display_date(image_id)
    modifier = 1

    if last_date_str:
        last_date = date.fromisoformat(last_date_str)
        days_since = (today - last_date).days
        modifier = 0.1 + 0.9 * (1 - math.exp(-days_since / 14))

    return modifier


# TODO
def weather_modifier(image_id: str, today: date) -> float:
    modifier = 1
    return modifier


def season_modifer(image_id: str, today: date) -> float:
    modifier = 1
    return modifier


def daytime_modifier(image_id: str, today: date) -> float:
    modifier = 1

    time = datetime.now().time()
    is_day = 6 <= time.hour < 18

    features = get_image_features(image_id)

    if is_day:
        modifier *= lerp(features.get("brightness", 0.5), 0.8, 1.3)
        modifier *= lerp(features.get("saturation", 0.5), 0.9, 1.2)
        modifier *= lerp(features.get("entropy", 0.5), 0.8, 1.2, invert=True)
        modifier *= lerp(features.get("contrast", 0.5), 0.9, 1.2)
    else:
        modifier *= lerp(features.get("brightness", 0.5), 0.8, 1.1, invert=True)
        modifier *= lerp(features.get("saturation", 0.5), 0.85, 1.1, invert=True)
        modifier *= lerp(features.get("entropy", 0.5), 0.9, 1.1)

    return modifier


def eink_modifier(image_id: str, today: date) -> float:
    modifier = 1
    return modifier


def compute_weight(img: Path, today: date) -> float:
    image_id = img.stem

    display_count = get_display_count(image_id)
    weight = 1 / math.sqrt(display_count + 1)

    weight *= cooldown_modifier(image_id, today)
    weight *= weather_modifier(image_id, today)
    weight *= season_modifer(image_id, today)
    weight *= daytime_modifier(image_id, today)
    weight *= eink_modifier(image_id, today)

    return weight


def choose_images(images, n: int, today: date) -> list[Path]:
    rng = random.Random(today.isoformat())
    raw_weights = [compute_weight(img, today) for img in images]
    scale = 100 / max(raw_weights, default=1)
    counts = [max(1, round(w * scale)) for w in raw_weights]

    return rng.sample(images, k=min(n, len(images)), counts=counts)


def random_image() -> Path:
    invalidate_cache()
    images = get_image_paths()
    if not images:
        images = [CONFIG.images.default_image]
    return random.choice(images)
