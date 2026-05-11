import logging
from pathlib import Path

from PIL import Image, ImageOps

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


def resize_image(
    source: Path,
    destination: Path,
    size: tuple[int, int],
) -> None:
    with Image.open(source) as img:
        result = (
            ImageOps.fit(img, size, method=Image.Resampling.LANCZOS)
            # .quantize(
            #     colors=6,
            #     method=Image.Quantize.MEDIANCUT,
            #     dither=Image.Dither.FLOYDSTEINBERG,
            # )
            .convert("RGB")
        )
        result.save(destination, format="JPEG", quality=95)
