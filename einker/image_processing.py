import colorsys
import logging
from pathlib import Path

import imagehash
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from einker.confparser import get_config
from einker.utils import lerp

logger = logging.getLogger(__name__)

CONFIG = get_config()


def validate_image(path: Path) -> tuple[bool, str | None]:
    try:
        with Image.open(path) as img:
            w, h = img.size

            if w < 800 or h < 480:
                return False, "Image too small."

            return True, None

    except Exception:
        return False, "Image invalid."


def enhance_image(img: Image) -> Image:

    enhancer = ImageEnhance.Contrast(img)
    result = enhancer.enhance(CONFIG.images.contrast)

    enhancer = ImageEnhance.Color(result)
    result = enhancer.enhance(CONFIG.images.saturation)

    enhancer = ImageEnhance.Sharpness(result)
    result = enhancer.enhance(CONFIG.images.sharpness)

    return result


# TODO
def quantize_image(img: Image) -> Image:
    return img


def resize_image(img: Image, size: tuple[int, int]) -> Image:
    return ImageOps.fit(img, size, method=Image.Resampling.LANCZOS)


def process_image(
    source: Path,
    destination: Path,
    size: tuple[int, int],
) -> None:
    with Image.open(source) as img:
        result = ImageOps.exif_transpose(img)

        result = resize_image(result, size)
        result = enhance_image(result)
        result = quantize_image(result)

        result = result.convert("RGB")
        result.save(destination, format="JPEG", quality=95)


def image_hash(path: Path) -> str:
    with Image.open(path) as img:
        return str(imagehash.phash(img))


def extract_color_features(path: Path) -> dict[str, float]:
    with Image.open(path) as img:
        img = img.convert("RGB")
        img.thumbnail((64, 64))
        pixels = list(img.getdata())

    total_pixels = len(pixels)

    reds = [p[0] for p in pixels]
    greens = [p[1] for p in pixels]
    blues = [p[2] for p in pixels]

    avg_r = sum(reds) / total_pixels
    avg_g = sum(greens) / total_pixels
    avg_b = sum(blues) / total_pixels

    brightness = (avg_r + avg_g + avg_b) / 3 / 255

    hue, saturation, _ = colorsys.rgb_to_hsv(
        avg_r / 255,
        avg_g / 255,
        avg_b / 255,
    )

    luminances = [(r + g + b) / 3 for r, g, b in pixels]

    avg_luminance = sum(luminances) / total_pixels

    variance = sum((lum - avg_luminance) ** 2 for lum in luminances) / total_pixels

    contrast = variance**0.5 / 255

    return {
        "brightness": brightness,
        "hue": hue,
        "saturation": saturation,
        "contrast": contrast,
    }


def edge_density(path: Path, threshold: int = 40) -> float:
    img = Image.open(path).convert("L")

    edges = img.filter(ImageFilter.FIND_EDGES)

    pixels = edges.load()

    width, height = edges.size
    edge_pixels = 0

    for y in range(height):
        for x in range(width):
            if pixels[x, y] > threshold:
                edge_pixels += 1

    return edge_pixels / (width * height)


def entropy(path: Path) -> float:
    with Image.open(path) as img:
        return img.entropy()
    return 0


def evaluate_eink_suitability(features: dict[str, float]):

    score = 1.0
    score *= lerp(features.get("entropy", 0.5), 0.7, 1.2, True)
    score *= lerp(features.get("edge_density", 0.5), 0.6, 1.2, True)
    score *= lerp(features.get("contrast", 0.5), 0.7, 1.3)

    status = "accepted" if score >= 0.5 else "rejected"

    return {
        "status": status,
        "score": score,
        "reason": (None if status == "accepted" else "automatic heuristic rejection"),
    }


def extract_all_features(path: Path) -> dict[str, float]:
    features = {
        **extract_color_features(path),
        "entropy": entropy(path),
        "edge_density": edge_density(path),
        "image_hash": image_hash(path),
    }

    return features
