import aiohttp
import asyncio
from typing import Optional, Tuple

API_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

WEATHER_CODES = {
    0: "Ясно",
    1: "Частичная облачность",
    2: "Облачно с прояснениями",
    3: "Пасмурно",
    45: "Туман",
    48: "Морозный туман",
    51: "Легкий моросящий дождь",
    53: "Моросящий дождь",
    55: "Сильный моросящий дождь",
    56: "Легкий ледяной дождь",
    57: "Сильный ледяной дождь",
    61: "Легкий дождь",
    63: "Дождь средней интенсивности",
    65: "Сильный дождь",
    66: "Легкий ледяной дождь",
    67: "Сильный ледяной дождь",
    71: "Легкий снег",
    73: "Снег средней интенсивности",
    75: "Сильный снег",
    77: "Снежные зерна",
    80: "Легкий дождь с грозой",
    81: "Дождь с грозой",
    82: "Сильный дождь с грозой",
    85: "Легкий снег с грозой",
    86: "Сильный снег с грозой",
    95: "Гроза",
    96: "Гроза с легким градом",
    99: "Гроза с сильным градом"
}


async def fetch_coordinates(city_name: str) -> tuple[float, float] | str:
    """Получить координаты города по названию."""
    url = f"{GEOCODING_URL}?name={city_name}&count=1&language=en&format=json"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                data = await response.json()
                if not data.get("results"):
                    return "Город не найден."
                result = data["results"][0]
                return result["latitude"], result["longitude"]
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        return f"Ошибка при запросе координат: {e}"


async def fetch_weather(lat: float, lon: float) -> str:
    """Получить текущий прогноз погоды по координатам."""
    url = (
        f"{API_URL}?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,weathercode&timezone=auto"
    )
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                data = await response.json()
                temp = data["current"]["temperature_2m"]
                code = data["current"]["weathercode"]
                description = WEATHER_CODES.get(code, "Неизвестный код погоды")
                return f"{temp}°C, {description}"
    except (aiohttp.ClientError, asyncio.TimeoutError, KeyError) as e:
        return f"Ошибка при получении прогноза: {e}"


async def get_weather_by_city(city_name: str) -> Tuple[str,
                                                       Optional[float],
                                                       Optional[float]]:
    """Получить прогноз и координаты по названию города."""
    coords = await fetch_coordinates(city_name)
    if isinstance(coords, str):
        return coords, None, None
    lat, lon = coords
    forecast = await fetch_weather(lat, lon)
    return forecast, lat, lon
