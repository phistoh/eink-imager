import tomllib
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]


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


def load_config(path: Path = Path("config.toml")) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def build_config(raw: dict) -> Config:
    paths = PathsConfig(
        image_dir=BASE_DIR / raw["paths"]["image-dir"],
        watch_dir=BASE_DIR / raw["paths"]["watch-dir"],
        processed_dir=BASE_DIR / raw["paths"]["processed-dir"],
        failed_dir=BASE_DIR / raw["paths"]["failed-dir"],
    )

    images = ImagesConfig(
        default_image=BASE_DIR / raw["images"]["default-image"],
        contrast=raw["images"]["contrast"],
        saturation=raw["images"]["saturation"],
        sharpness=raw["images"]["sharpness"],
    )

    app = AppConfig(
        cache_ttl=raw["app"]["cache-ttl"],
        images_per_day=raw["app"]["images-per-day"],
        debug=raw["app"]["debug"],
    )

    return Config(paths=paths, images=images, app=app)


CONFIG = build_config(load_config(BASE_DIR / "config.toml"))
