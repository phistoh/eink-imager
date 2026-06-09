import math


def lerp(
    value: float,
    low: float,
    high: float,
    invert: bool = False,
) -> float:
    value = max(0.0, min(1.0, value))

    if invert:
        value = 1.0 - value

    return low + value * (high - low)


def circular_distance(a: float, b: float, circumference: float = 1.0) -> float:
    d = abs(a - b)
    return min(d, circumference - d)


def gaussian_similarity(
    x: float,
    sigma: float,
) -> float:
    """Calculates a weight depending on a bell curve.
    Since it is not a probability distribution, both the expected value `my`
    and the normalization `1/(sigma*sqrt(2pi))` are not present."""

    return math.exp(-(x**2) / (2 * sigma**2))


def hue_preference(
    hue: float,
    target: float,
    sigma: float = 0.1,
) -> float:
    distance = circular_distance(hue, target)

    return gaussian_similarity(distance, sigma)
