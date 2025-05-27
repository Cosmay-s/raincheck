from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import City


async def get_or_create_city(session: AsyncSession, name: str,
                             latitude: float, longitude: float) -> City:
    """
    Получить город по координатам или создать новый с начальным счетчиком 1.
    """
    result = await session.execute(
        select(City).where(
            and_(City.latitude == latitude, City.longitude == longitude)
        )
    )
    city = result.scalar_one_or_none()
    if not city:
        city = City(name=name, latitude=latitude, longitude=longitude,
                    search_count=0)
        session.add(city)
        await session.flush()
    return city


async def increment_search_count(session: AsyncSession, city_id: int):
    """
    Увеличить счетчик поисков для города по его ID.
    """
    result = await session.execute(select(City).where(City.id == city_id))
    city = result.scalar_one()
    city.search_count += 1
    session.add(city)


async def get_top_cities(session: AsyncSession, limit: int = 5):
    """
    Получить список названий городов с наибольшим количеством поисков.
    """
    result = await session.execute(
        select(City.name, City.search_count)
        .order_by(City.search_count.desc())
        .limit(limit)
    )
    return [{"city": name, "count": count} for name, count in result.fetchall()]
