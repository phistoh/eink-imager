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


def hue_distance(a: float, b: float) -> float:
    d = abs(a - b)
    return min(d, 1.0 - d)


def hue_preference(
    hue: float,
    target: float,
    sigma: float = 0.1,
) -> float:
    distance = hue_distance(hue, target)

    return math.exp(-(distance**2) / (2 * sigma**2))
