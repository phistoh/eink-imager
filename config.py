from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent

######################
# Config starts here #
######################

# Image
IMAGE_DIR = BASE_DIR / "static/images"
DEFAULT_IMAGE = BASE_DIR / "static/images/default.jpg"

# Caching
CACHE_TTL = timedelta(hours=24)

# File handling
WATCH_DIR = BASE_DIR / Path("test/incoming")
PROCESSED_DIR = Path("test/processed")
FAILED_DIR = Path("test/failed")
