from fastapi import FastAPI, Request, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import os
import base64

from app.weather import get_weather_by_city
from app.repository import get_top_cities_repo, process_city_search_repo, search_cities_by_prefix

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))


@app.on_event("startup")
async def on_startup():
    """Инициализация базы данных при старте приложения."""
    from app.database import init_db
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

    top_cities = await get_top_cities_repo(limit=5)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "forecast": None,
        "city": recent_city,
        "search_count": None,
        "top_cities": top_cities,
        "error": None
    })


@app.post("/", response_class=HTMLResponse)
async def get_weather(request: Request, city: str = Form(...)):
    """
    Обработка формы с названием города.

    Получает погоду, обновляет статистику поиска и отображает результат.
    """
    forecast, latitude, longitude = await get_weather_by_city(city)

    if latitude is None or longitude is None:
        top_cities = await get_top_cities_repo(limit=5)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "forecast": None,
            "city": city,
            "search_count": None,
            "top_cities": top_cities,
            "error": "Не удалось получить координаты для города. Попробуйте другой город."
        })

    city_obj, count, top_cities = await process_city_search_repo(city, latitude, longitude)

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


@app.get("/api/cities", response_class=JSONResponse)
async def autocomplete_cities(q: str = Query(..., min_length=1)):
    """
    Возвращает список городов, начинающихся на q (часть названия).
    """
    cities = await search_cities_by_prefix(q)
    return JSONResponse(content=cities)
