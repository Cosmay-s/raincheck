from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import City, SearchCount


async def get_or_create_city(session: AsyncSession, city_name: str) -> City:
    city_name = city_name.strip().lower()
    stmt = select(City).where(City.name == city_name)
    result = await session.execute(stmt)
    city = result.scalar_one_or_none()
    if city:
        return city
    city = City(name=city_name)
    session.add(city)
    await session.commit()
    await session.refresh(city)
    return city


async def increment_search_count(session: AsyncSession, city_id: int):
    stmt = select(SearchCount).where(SearchCount.city_id == city_id)
    result = await session.execute(stmt)
    search_count = result.scalar_one_or_none()

    if search_count:
        search_count.count += 1
        session.add(search_count)
    else:
        search_count = SearchCount(city_id=city_id, count=1)
        session.add(search_count)
    await session.commit()


async def get_search_counts(session: AsyncSession):
    stmt = (
        select(City.name, SearchCount.count)
        .join(SearchCount, City.id == SearchCount.city_id)
    )
    result = await session.execute(stmt)
    return result.all()
