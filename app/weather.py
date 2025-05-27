import aiohttp
import asyncio

API_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


class GeocodingError(Exception):
    """Исключение при ошибках геокодинга (получение координат города)."""
    pass


class WeatherFetchError(Exception):
    """Исключение при ошибках получения прогноза погоды."""
    pass


async def fetch_coordinates(city_name: str) -> tuple[float, float]:
    """
    Получить широту и долготу города по его названию.

    Args:
        city_name (str): Название города (лучше на английском для надежности).

    Returns:
        tuple[float, float]: Координаты (широта, долгота).

    Raises:
        GeocodingError: Если город не найден или произошла ошибка запроса.
    """
    url = f"{GEOCODING_URL}?name={city_name}&count=1&language=en&format=json"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                data = await response.json()
                if not data.get("results"):
                    raise GeocodingError("Город не найден.")

                result = data["results"][0]
                return result["latitude"], result["longitude"]
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        raise GeocodingError(f"Ошибка при запросе координат: {e}")


async def fetch_weather(lat: float, lon: float) -> str:
    """
    Получить текущий прогноз погоды по координатам.

    Args:
        lat (float): Широта.
        lon (float): Долгота.

    Returns:
        str: Текст с температурой и кодом погоды.

    Raises:
        WeatherFetchError: Если произошла ошибка при запросе
        прогноза или обработке данных.
    """
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
                return f"{temp}°C, код погоды: {code}"
    except (aiohttp.ClientError, asyncio.TimeoutError, KeyError) as e:
        raise WeatherFetchError(f"Ошибка при получении прогноза: {e}")


async def get_weather_by_city(city_name: str) -> str:
    """
    Получить прогноз погоды по названию города.

    Выполняет последовательный запрос координат, затем прогноза.
    Обрабатывает ошибки и возвращает текст с информацией или ошибкой.

    Args:
        city_name (str): Название города.

    Returns:
        str: Прогноз погоды или сообщение об ошибке.
    """
    try:
        lat, lon = await fetch_coordinates(city_name)
        forecast = await fetch_weather(lat, lon)
        return forecast
    except GeocodingError as ge:
        return str(ge)
    except WeatherFetchError as we:
        return str(we)
