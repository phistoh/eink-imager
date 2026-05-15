import logging
import os
import tomllib
from dataclasses import dataclass
from functools import cache
from pathlib import Path

logger = logging.getLogger(__name__)


def resolve_path(path: str) -> Path:
    einker_root = Path(
        os.environ.get("APP_BASE_DIR", str(Path(__file__).resolve().parents[1]))
    )
    return einker_root / path


@dataclass
class PathsConfig:
    image_dir: Path
    watch_dir: Path
    processed_dir: Path
    failed_dir: Path


@dataclass
class ImagesConfig:
    default_image: Path
    contrast: float
    saturation: float
    sharpness: float


@dataclass
class AppConfig:
    cache_ttl: int
    images_per_day: int
    debug: bool


@dataclass
class Config:
    paths: PathsConfig
    images: ImagesConfig
    app: AppConfig


def load_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing config file: {path}")

    with open(path, "rb") as f:
        return tomllib.load(f)


def build_config(raw: dict) -> Config:
    paths = PathsConfig(
        image_dir=resolve_path(raw["paths"]["image-dir"]),
        watch_dir=resolve_path(raw["paths"]["watch-dir"]),
        processed_dir=resolve_path(raw["paths"]["processed-dir"]),
        failed_dir=resolve_path(raw["paths"]["failed-dir"]),
    )

    images = ImagesConfig(
        default_image=resolve_path(raw["images"]["default-image"]),
        contrast=float(os.getenv("EINKER_CONTRAST", raw["images"]["contrast"])),
        saturation=float(os.getenv("EINKER_SATURATION", raw["images"]["saturation"])),
        sharpness=float(os.getenv("EINKER_SHARPNESS", raw["images"]["sharpness"])),
    )

    app = AppConfig(
        cache_ttl=raw["app"]["cache-ttl"],
        images_per_day=int(
            os.getenv("EINKER_IMAGES_PER_DAY", raw["app"]["images-per-day"])
        ),
        debug=raw["app"]["debug"],
    )

    return Config(paths=paths, images=images, app=app)


@cache
def get_config():
    return build_config(load_config(resolve_path("settings.toml")))
