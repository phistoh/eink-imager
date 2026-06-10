import logging
import os
import sys
from pathlib import Path

from einker.confparser import get_config
from einker.file_handling import get_image_path_by_id
from einker.image_processing import evaluate_eink_suitability, extract_all_features
from einker.metadata import (
    add_image_color_features,
    add_image_feature,
    find_duplicate_images,
    get_image_features,
    get_images_with_missing_feature,
    get_images_with_missing_hash,
    get_images_without_eink_evaluation,
    init_db,
    migrate_db,
    set_eink_evaluation,
    set_image_hash,
)
from einker.weather import update_weather_cache

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
        case "image_hash":
            images = get_images_with_missing_hash()
            for (image_id,) in images:
                features = extract_all_features(get_image_path_by_id(image_id))
                duplicates = find_duplicate_images(features["image_hash"])

                if duplicates and duplicates["id"] != image_id:
                    logger.warning(
                        "Backfill skip: %s duplicates existing image %s",
                        image_id,
                        duplicates["id"],
                    )
                    continue

                set_image_hash(image_id, features["image_hash"])
                logger.info(
                    "Backfilled image hash for image %s: %s",
                    image_id,
                    features[feature_name],
                )
        case "color_features":
            images = set()
            images.update(get_images_with_missing_feature("brightness"))
            images.update(get_images_with_missing_feature("hue"))
            images.update(get_images_with_missing_feature("saturation"))
            images.update(get_images_with_missing_feature("contrast"))

            for (image_id,) in images:
                features = extract_all_features(get_image_path_by_id(image_id))
                add_image_color_features(image_id, features)
                logger.info(
                    "Backfilled color features for image %s: %s", image_id, features
                )
        case "entropy" | "edge_density":
            images = get_images_with_missing_feature(feature_name)
            for (image_id,) in images:
                features = extract_all_features(get_image_path_by_id(image_id))
                add_image_feature(image_id, feature_name, features[feature_name])
                logger.info(
                    "Backfilled %s for image %s: %s",
                    feature_name,
                    image_id,
                    features[feature_name],
                )


def backfill_eink_evaluations() -> None:
    rows = get_images_without_eink_evaluation()

    logger.info(
        "Backfilling %s missing e-ink evaluations",
        len(rows),
    )
    for row in rows:
        image_id = row["id"]
        features = get_image_features(image_id)

        required = {
            "entropy",
            "edge_density",
            "contrast",
        }

        if not required.issubset(features):
            logger.warning(
                "Skipping e-ink evaluation for '%s': missing features",
                image_id,
            )
            continue

        evaluation = evaluate_eink_suitability(features)

        set_eink_evaluation(
            image_id,
            evaluation["status"],
            evaluation["score"],
            evaluation["reason"],
        )

        logger.info(
            "Backfilled e-ink evaluation for '%s': %s (%.2f)",
            image_id,
            evaluation["status"],
            evaluation["score"],
        )


def backfill_features():
    backfill_feature("image_hash")
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
    prepare_filesystem()
    init_db()
    migrate_db()
    backfill_features()
    try:
        update_weather_cache()
    except Exception as e:
        logger.warning(
            "Could not update weather cache: %s",
            e,
        )
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
