import argparse
import subprocess

from einker.confparser import get_config
from einker.image_processing import evaluate_eink_suitability
from einker.metadata import (
    FEATURE_VERSION,
    LATEST_SCHEMA_VERSION,
    count_accepted_images,
    count_images,
    count_rejected_images,
    delete_image,
    get_all_image_ids,
    get_image,
    get_image_features,
    get_images_with_missing_hash,
    get_images_without_eink_evaluation,
    set_eink_evaluation,
)

CONFIG = get_config()

RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"


def delete_image_everywhere(image_id: str) -> None:
    image = get_image(image_id)

    if not image:
        print(f"Image {image_id} not found")
        return

    processed_name = image["processed_name"]

    paths = [
        CONFIG.paths.processed_dir / processed_name,
        CONFIG.paths.image_dir / processed_name,
    ]

    for path in paths:
        if path.exists():
            path.unlink()

    delete_image(image_id)

    print(f"Deleted image {image_id}")


def show_image(image_id: str) -> None:
    image = get_image(image_id)

    if not image:
        print(f"Image '{image_id}' not found")
        return

    path = CONFIG.paths.image_dir / image["processed_name"]

    # render preview
    subprocess.run(
        [
            "magick",
            str(path),
            "-geometry",
            "600x360>",
            "sixel:-",
        ],
        stderr=subprocess.DEVNULL,
        check=True,
    )

    features = get_image_features(image_id)

    print()
    print(f"Image ID: {image_id}")
    print()

    print("Metadata")
    print("--------")
    print(f"Original name : {image['original_name']}")
    print(f"Processed name: {image['processed_name']}")
    print(f"Created at    : {image['created_at']}")
    print(f"Hash          : {image['image_hash']}")
    print()

    print("E-ink")
    print("------")

    status = image["eink_status"]
    color = GREEN
    if status == "rejected":
        color = RED

    print(f"Status: {color}{status}{RESET}")
    print(f"Score : {image['eink_score']}")
    print(f"Reason: {image['eink_reason']}")
    print()

    print("Features")
    print("--------")

    for key, value in features.items():
        if key in ("image_id", "feature_version"):
            continue

        print(f"{key:14}: {value}")


def reevaluate_images() -> None:
    image_ids = get_all_image_ids()

    for image_id in image_ids:
        features = get_image_features(image_id)

        evaluation = evaluate_eink_suitability(features)

        image = get_image(image_id)

        old_status = image["eink_status"]
        old_score = image["eink_score"]

        set_eink_evaluation(
            image_id,
            evaluation["status"],
            evaluation["score"],
            evaluation["reason"],
        )

        if old_status != evaluation["status"] or round(old_score or 0, 2) != round(
            evaluation["score"], 2
        ):
            print(
                f"{image_id}: {old_status} -> {evaluation['status']} ({old_score or 0} -> {evaluation['score']})"
            )


def show_stats() -> None:
    total = count_images()
    accepted = count_accepted_images()
    rejected = count_rejected_images()

    missing_hashes = len(get_images_with_missing_hash())
    missing_evaluations = len(get_images_without_eink_evaluation())

    print()
    print("Images")
    print("------")
    print(f"Total images        : {total}")
    print(f"Accepted            : {accepted}")
    print(f"Rejected            : {rejected}")
    print()

    print("Features")
    print("--------")
    print(f"Missing hashes      : {missing_hashes}")
    print(f"Missing evaluations : {missing_evaluations}")
    print()

    print("Database")
    print("--------")
    print(f"Schema version      : {LATEST_SCHEMA_VERSION}")
    print(f"Feature version     : {FEATURE_VERSION}")


def main():
    parser = argparse.ArgumentParser(
        prog="einker",
        description="Administrative CLI for E-Inker",
    )

    sub = parser.add_subparsers(
        required=True,
    )

    delete_parser = sub.add_parser(
        "delete",
        help="Delete an image and its metadata",
    )
    delete_parser.add_argument(
        "image_id",
        help="ID of the image to delete",
    )
    delete_parser.set_defaults(func=lambda args: delete_image_everywhere(args.image_id))

    show_parser = sub.add_parser(
        "show",
        help="Show image preview and metadata",
    )
    show_parser.add_argument(
        "image_id",
        help="ID of the image to display",
    )
    show_parser.set_defaults(func=lambda args: show_image(args.image_id))

    reevaluate_parser = sub.add_parser(
        "reevaluate",
        help="Recalculate e-ink suitabilities",
    )
    reevaluate_parser.set_defaults(func=lambda args: reevaluate_images())

    stats_parser = sub.add_parser(
        "stats",
        help="Show collection statistics",
    )
    stats_parser.set_defaults(func=lambda args: show_stats())

    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main()
