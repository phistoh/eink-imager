import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


BASE_DIR = Path(os.environ.get("APP_BASE_DIR", Path(__file__).resolve().parents[1]))
INITIALIZED_MARKER = BASE_DIR / "data/.initialized"


class PreflightError(RuntimeError):
    pass


def ready_check():
    if not INITIALIZED_MARKER.exists():
        raise PreflightError(
            "⚠️ **eink-imager** not initialized. Please run 'make init' first."
        )
