from pathlib import Path

from einker.confparser import get_config
from einker.metadata import init_db

CONFIG = get_config()


def prepare_filesystem():
    paths = [
        CONFIG.paths.image_dir,
        CONFIG.paths.watch_dir,
        CONFIG.paths.processed_dir,
        CONFIG.paths.failed_dir,
    ]

    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    init_db()
    prepare_filesystem()
