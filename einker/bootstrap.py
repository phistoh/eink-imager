import logging
import os
import sys
from pathlib import Path

from einker.confparser import get_config
from einker.metadata import init_db, migrate_db

logger = logging.getLogger(__name__)


CONFIG = get_config()


class PreflightError(RuntimeError):
    pass


def prepare_filesystem():
    paths = [
        CONFIG.paths.image_dir,
        CONFIG.paths.watch_dir,
        CONFIG.paths.processed_dir,
        CONFIG.paths.failed_dir,
    ]

    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)


def initialize():
    prepare_filesystem()
    init_db()
    migrate_db()


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


def bootstrap():
    initialize()
    ready_check()


if __name__ == "__main__":
    try:
        bootstrap()

    except PreflightError as e:
        logger.error(str(e))
        sys.exit(1)

    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
