import logging
import os
from pathlib import Path

from einker.confparser import get_config

logger = logging.getLogger(__name__)


CONFIG = get_config()


class PreflightError(RuntimeError):
    pass


def check_directory(path: Path, name: str) -> None:
    if not path.exists():
        raise PreflightError(f"{name} does not exist: {path}")

    if not path.is_dir():
        raise PreflightError(f"{name} is not a directory: {path}")

    if not os.access(path, os.R_OK | os.W_OK):
        raise PreflightError(f"{name} is not readable/writable: {path}")


def ready_check() -> None:
    check_directory(CONFIG.paths.data_dir, "Data directory")
    check_directory(CONFIG.paths.image_dir, "Image directory")
    check_directory(CONFIG.paths.watch_dir, "Watch directory")
    check_directory(CONFIG.paths.processed_dir, "Processed directory")
    check_directory(CONFIG.paths.failed_dir, "Failed directory")


if __name__ == "__main__":
    ready_check()
