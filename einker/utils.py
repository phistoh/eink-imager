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


def gaussian_score(value, ideal, sigma):
    return math.exp(-((value - ideal) ** 2) / (2 * sigma**2))
