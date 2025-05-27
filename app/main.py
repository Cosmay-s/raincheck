from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
from app.weather import get_weather_by_city  # Импортируем функцию получения погоды

app = FastAPI()

# Инициализация объекта Jinja2Templates для работы с HTML-шаблонами
# Указываем путь к папке с шаблонами относительно текущего файла
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__),
                                                   "templates"))


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Обработчик GET-запроса на корень сайта ("/").

    Параметры:
        request (Request): объект запроса,
        необходимый для корректной работы шаблонов Jinja2.

    Возвращает:
        HTML-страницу с формой для ввода города.
        В шаблон передаются пустые значения для прогноза погоды.
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "forecast": None,  # Пока нет прогноза
            "city": None       # Пока не выбран город
        }
    )

@app.post("/", response_class=HTMLResponse)
async def get_weather(request: Request, city: str = Form(...)):
    """
    Обработчик POST-запроса на корень сайта ("/").
    Получает название города из формы, запрашивает прогноз погоды,
    и возвращает HTML-страницу с результатом.

    Параметры:
        request (Request): объект запроса, необходимый для шаблонов Jinja2.
        city (str): название города, полученное из данных формы (обязательное).

    Возвращает:
        HTML-страницу с заполненным прогнозом погоды и названием города.
    """
    # Получаем прогноз погоды асинхронно, вызывая функцию из модуля weather
    forecast = await get_weather_by_city(city)

    # Возвращаем шаблон с прогнозом и названием города
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "forecast": forecast,
            "city": city
        }
    )
