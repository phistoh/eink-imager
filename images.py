import logging
import random
from datetime import date
from pathlib import Path

from file_handling import get_image_paths

logger = logging.getLogger(__name__)


def get_daily_image() -> Path:
    images = get_image_paths()
    seed = date.today().isoformat()
    rng = random.Random(seed)
    return rng.choice(images)


def get_random_image() -> Path:
    images = get_image_paths()
    return random.choice(images)
