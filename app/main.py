from fastapi import FastAPI, Request, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import os
import base64

from app.weather import get_weather_by_city
from app.database import async_session, init_db
from app.crud import get_or_create_city, increment_search_count, get_top_cities
from sqlalchemy import select
from app.models import City

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__),
                                                   "templates"))


@app.on_event("startup")
async def on_startup():
    """
    Инициализация базы данных — создание всех таблиц при старте приложения.
    """
    await init_db()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Главная страница.

    Показывает последние популярные города и погоду для последнего
    запрошенного города (если есть).
    """
    last_city = request.cookies.get("last_city")
    recent_city = None

    if last_city:
        try:
            recent_city = base64.b64decode(last_city.encode("ascii")).decode("utf-8")
        except Exception:
            recent_city = None

    async with async_session() as session:
        top_cities = await get_top_cities(session, limit=5)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "forecast": None,
        "city": recent_city,
        "search_count": None,
        "top_cities": top_cities
    })

@app.post("/", response_class=HTMLResponse)
async def get_weather(request: Request, city: str = Form(...)):
    """
    Обработка формы с названием города.

    Получает погоду, обновляет статистику поиска в базе и отображает данные.
    """
    forecast, latitude, longitude = await get_weather_by_city(city)

    if latitude is None or longitude is None:
        async with async_session() as session:
            top_cities = await get_top_cities(session, limit=5)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "forecast": None,
            "city": city,
            "search_count": None,
            "top_cities": top_cities,
            "error": "Не удалось получить координаты для города. Попробуйте другой город."
        })

    async with async_session() as session:
        async with session.begin():
            city_obj = await get_or_create_city(session, city,
                                                latitude, longitude)
            await increment_search_count(session, city_obj.id)
            count = city_obj.search_count

        top_cities = await get_top_cities(session, limit=5)

    response = templates.TemplateResponse("index.html", {
        "request": request,
        "forecast": forecast,
        "city": city,
        "search_count": count,
        "top_cities": top_cities,
        "error": None
    })

    encoded_city = base64.b64encode(city.encode("utf-8")).decode("ascii")
    response.set_cookie("last_city", encoded_city, max_age=60*60*24*30)

    return response


@app.get("/api/stats")
async def stats():
    """
    API для получения статистики популярных городов.

    Возвращает JSON с городами и количеством запросов, отсортированный по убыванию.
    """
    async with async_session() as session:
        result = await session.execute(
            select(City.name, City.search_count)
            .order_by(City.search_count.desc())
        )
        data = [{"city": name, "count": count} for name, count in result.fetchall()]
        return JSONResponse(content=data)


@app.get("/api/cities")
async def autocomplete_cities(q: str = Query(..., min_length=1)):
    """
    Возвращает список городов, начинающихся на q (часть названия).
    """
    async with async_session() as session:
        result = await session.execute(
            select(City.name)
            .where(City.name.ilike(f"{q}%"))
            .order_by(City.search_count.desc())
            .limit(10)
        )
        cities = result.scalars().all()
    return JSONResponse(content=cities)
