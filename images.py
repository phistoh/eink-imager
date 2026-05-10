import random
from datetime import date

import config
from file_handling import get_image_paths


def get_daily_image():
    images = get_image_paths()
    seed = date.today().isoformat()
    rng = random.Random(seed)
    return rng.choice(images)


def get_random_image():
    images = get_image_paths()
    return random.choice(images)
