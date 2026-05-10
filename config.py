from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent

######################
# Config starts here #
######################

# Image
IMAGE_DIR = BASE_DIR / "static/images"
DEFAULT_IMAGE = BASE_DIR / "static/default.jpg"

# Caching
CACHE_TTL = timedelta(hours=24)
DEFAULT_IMAGE = Path("static/default.jpg")
