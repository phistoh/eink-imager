import logging
import os
import sys
from pathlib import Path

from einker.confparser import get_config
from einker.file_handling import get_image_path_by_id
from einker.image_processing import edge_density, entropy, extract_color_features
from einker.metadata import (
    add_image_color_features,
    add_image_feature,
    get_images_with_missing_feature,
    get_images_with_missing_hash,
    init_db,
    migrate_db,
)

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


def backfill_feature(feature_name: str) -> None:
    match feature_name:
        case "hash":
            images = get_images_with_missing_hash()
            for image in images:
                image_id = image[0]
                # todo
        case "color_features":
            images = []
            images += get_images_with_missing_feature("brightness")
            images += get_images_with_missing_feature("hue")
            images += get_images_with_missing_feature("saturation")
            images += get_images_with_missing_feature("contrast")
            for image in images:
                image_id = image[0]
                features = extract_color_features(get_image_path_by_id(image_id))
                add_image_color_features(image_id, features)
                logger.info(
                    "Backfilled color features for image %s: %s", image_id, features
                )
        case "entropy":
            images = get_images_with_missing_feature("entropy")
            for image in images:
                image_id = image[0]
                value = entropy(get_image_path_by_id(image_id))
                add_image_feature(image_id, "entropy", value)
                logger.info("Backfilled entropy for image %s: %s", image_id, value)
        case "edge_density":
            images = get_images_with_missing_feature("edge_density")
            for image in images:
                image_id = image[0]
                value = edge_density(get_image_path_by_id(image_id))
                add_image_feature(image_id, "edge_density", value)
                logger.info("Backfilled edge_density for image %s: %s", image_id, value)


def initialize():
    prepare_filesystem()
    init_db()
    migrate_db()
    backfill_feature("hash")
    backfill_feature("color_features")
    backfill_feature("entropy")
    backfill_feature("edge_density")


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
