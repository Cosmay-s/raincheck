from sqlalchemy import select
from app.database import async_session
from app.crud import get_or_create_city, increment_search_count, get_top_cities
from app.models import City


async def get_top_cities_repo(limit: int = 5):
    """
    Получить список топовых городов по количеству запросов.
    """
    async with async_session() as session:
        return await get_top_cities(session, limit=limit)


async def process_city_search_repo(city_name: str, latitude: float,
                                   longitude: float):
    """
    Обработка поиска города:
    - найти или создать город в базе,
    - увеличить счётчик запросов,
    - получить топ городов.
    """
    async with async_session() as session:
        async with session.begin():
            city_obj = await get_or_create_city(session, city_name,
                                                latitude, longitude)
            await increment_search_count(session, city_obj.id)
            count = city_obj.search_count
        top_cities = await get_top_cities(session, limit=5)
    return city_obj, count, top_cities


async def search_cities_by_prefix(prefix: str, limit: int = 10):
    """
    Получить список городов, начинающихся с префикса `prefix`.
    """
    async with async_session() as session:
        result = await session.execute(
            select(City.name)
            .where(City.name.ilike(f"{prefix}%"))
            .order_by(City.search_count.desc())
            .limit(limit)
        )
        cities = result.scalars().all()
    return cities

