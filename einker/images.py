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
from einker.utils import hue_preference, lerp

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
    features = get_image_features(image_id)

    brightness = features.get("brightness", 0.5)
    saturation = features.get("saturation", 0.5)
    entropy = features.get("entropy", 0.5)
    contrast = features.get("contrast", 0.5)
    hue = features.get("hue", 0.5)

    month = today.month

    # SPRING
    if month in [3, 4, 5]:
        hue_score = hue_preference(
            hue,
            target=0.33,
            sigma=0.12,
        )

        brightness_score = lerp(
            brightness,
            0.9,
            1.1,
        )

        saturation_score = lerp(
            saturation,
            0.95,
            1.15,
        )

        entropy_score = lerp(
            entropy,
            0.95,
            1.05,
        )

        contrast_score = lerp(
            contrast,
            0.95,
            1.05,
        )

        modifier = (
            hue_score * 0.45
            + saturation_score * 0.20
            + brightness_score * 0.20
            + entropy_score * 0.10
            + contrast_score * 0.05
        )

    # SUMMER
    elif month in [6, 7, 8]:
        hue_score = 1.0

        brightness_score = lerp(
            brightness,
            0.9,
            1.2,
        )

        saturation_score = lerp(
            saturation,
            0.9,
            1.25,
        )

        entropy_score = lerp(
            entropy,
            0.95,
            1.1,
        )

        contrast_score = lerp(
            contrast,
            0.95,
            1.15,
        )

        modifier = (
            saturation_score * 0.35
            + brightness_score * 0.30
            + contrast_score * 0.20
            + hue_score * 0.10
            + entropy_score * 0.05
        )

    # AUTUMN
    elif month in [9, 10, 11]:
        hue_score = hue_preference(
            hue,
            target=0.10,
            sigma=0.08,
        )

        brightness_score = lerp(
            brightness,
            0.9,
            1.0,
            invert=True,
        )

        saturation_score = lerp(
            saturation,
            0.9,
            1.05,
        )

        entropy_score = lerp(
            entropy,
            0.9,
            1.05,
            invert=True,
        )

        contrast_score = lerp(
            contrast,
            0.95,
            1.1,
        )

        modifier = (
            hue_score * 0.55
            + saturation_score * 0.15
            + brightness_score * 0.10
            + entropy_score * 0.10
            + contrast_score * 0.10
        )

    # WINTER
    else:
        hue_score = hue_preference(
            hue,
            target=0.60,
            sigma=0.10,
        )

        brightness_score = lerp(
            brightness,
            0.95,
            1.15,
        )

        saturation_score = lerp(
            saturation,
            0.85,
            1.05,
            invert=True,
        )

        entropy_score = lerp(
            entropy,
            0.9,
            1.05,
            invert=True,
        )

        contrast_score = lerp(
            contrast,
            0.95,
            1.05,
        )

        modifier = (
            hue_score * 0.35
            + brightness_score * 0.25
            + saturation_score * 0.20
            + entropy_score * 0.15
            + contrast_score * 0.05
        )

    return modifier


def daytime_modifier(image_id: str) -> float:
    modifier = 1

    time = datetime.now().time()
    is_day = 6 <= time.hour < 18

    features = get_image_features(image_id)

    if is_day:
        brightness_score = lerp(features.get("brightness", 0.5), 0.8, 1.3)
        saturation_score = lerp(features.get("saturation", 0.5), 0.9, 1.2)
        entropy_score = lerp(features.get("entropy", 0.5), 0.8, 1.2, invert=True)
        contrast_score = lerp(features.get("contrast", 0.5), 0.9, 1.2)

        modifier = (
            brightness_score * 0.4
            + saturation_score * 0.2
            + entropy_score * 0.3
            + contrast_score * 0.1
        )

    else:
        brightness_score = lerp(features.get("brightness", 0.5), 0.8, 1.1, invert=True)
        saturation_score = lerp(features.get("saturation", 0.5), 0.85, 1.1, invert=True)
        entropy_score = lerp(features.get("entropy", 0.5), 0.9, 1.1)

        modifier = brightness_score * 0.3 + saturation_score * 0.4 + entropy_score * 0.3

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
    weight *= daytime_modifier(image_id)
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
