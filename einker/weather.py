import json
import logging
from datetime import datetime
from enum import StrEnum
from pathlib import Path

import requests

from einker.confparser import get_config

logger = logging.getLogger(__name__)

CONFIG = get_config()

BASE_DIR = Path(__file__).resolve().parents[1]
WEATHER_CACHE = BASE_DIR / "data" / "weather.json"

FOG_CODES = {
    45,
    48,
}

RAIN_CODES = {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99}

SNOW_CODES = {
    71,
    73,
    75,
    77,
    85,
    86,
}

CLOUDY_CODES = {
    1,
    2,
    3,
}


class Weather(StrEnum):
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAIN = "rain"
    FOG = "fog"
    SNOW = "snow"


def get_weather_code() -> int:
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": CONFIG.weather.latitude,
            "longitude": CONFIG.weather.longitude,
            "current": "weather_code",
        },
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    return data["current"]["weather_code"]


def weather_category(code: int) -> Weather:
    if code == 0:
        return Weather.SUNNY

    if code in FOG_CODES:
        return Weather.FOG

    if code in RAIN_CODES:
        return Weather.RAIN

    if code in SNOW_CODES:
        return Weather.SNOW

    if code in CLOUDY_CODES:
        return Weather.CLOUDY

    logger.warning("Unknown WMO weather code: %s; treating as cloudy", code)

    return Weather.CLOUDY


def update_weather_cache() -> None:
    code = get_weather_code()
    weather = weather_category(code)

    payload = {
        "weather": weather.value,
        "wmo_code": code,
        "updated_at": datetime.now().isoformat(),
    }

    WEATHER_CACHE.parent.mkdir(parents=True, exist_ok=True)

    with WEATHER_CACHE.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    logger.info(
        "Updated weather cache: %s (WMO code %s)",
        weather.value,
        code,
    )


def current_weather() -> Weather:
    try:
        with WEATHER_CACHE.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return Weather(data["weather"])

    except FileNotFoundError:
        logger.warning("Weather cache missing")
        return Weather.CLOUDY
