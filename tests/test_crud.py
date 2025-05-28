import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import get_or_create_city, increment_search_count, get_top_cities
from app.database import async_session, init_db
from app.models import City

@pytest.fixture(scope="module", autouse=True)
async def prepare_db():
    await init_db()
    yield

@pytest.mark.asyncio
async def test_get_or_create_city_creates_and_gets():
    async with async_session() as session:
        city1 = await get_or_create_city(session, "TestCity", 10.0, 20.0)
        assert city1.name == "TestCity"
        assert city1.search_count == 0

        city2 = await get_or_create_city(session, "TestCity", 10.0, 20.0)
        assert city1.id == city2.id  # должен вернуть ту же запись

@pytest.mark.asyncio
async def test_increment_search_count_increases():
    async with async_session() as session:
        city = await get_or_create_city(session, "CounterCity", 11.0, 21.0)
        await increment_search_count(session, city.id)
        await session.commit()

        result = await session.get(City, city.id)
        assert result.search_count == city.search_count + 1

@pytest.mark.asyncio
async def test_get_top_cities_returns_sorted():
    async with async_session() as session:
        # Добавим несколько городов с разным счетчиком
        for i in range(5):
            city = await get_or_create_city(session, f"City{i}", i, i)
            city.search_count = i
            session.add(city)
        await session.commit()

        top_cities = await get_top_cities(session, limit=3)
        assert len(top_cities) == 3
        counts = [c['count'] for c in top_cities]
        assert counts == sorted(counts, reverse=True)
