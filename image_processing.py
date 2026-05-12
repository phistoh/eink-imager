import logging
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

import config

logger = logging.getLogger(__name__)


def validate_image(path: Path) -> tuple[bool, str | None]:
    try:
        with Image.open(path) as img:
            w, h = img.size

            if w < 800 or h < 480:
                return False, "Image too small."

            return True, None

    except Exception as e:
        return False, "Image invalid."


def enhance_image(img: Image) -> Image:

    enhancer = ImageEnhance.Contrast(img)
    result = enhancer.enhance(config.CONTRAST)

    enhancer = ImageEnhance.Color(result)
    result = enhancer.enhance(config.SATURATION)

    enhancer = ImageEnhance.Sharpness(result)
    result = enhancer.enhance(config.SHARPNESS)

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
