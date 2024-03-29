import logging
from http import HTTPStatus
from typing import List, Literal
from uuid import UUID

from core.config import ErrorMessage
from fastapi import APIRouter, Depends, HTTPException, Query
from models.film import FilmApi, FilmBriefApi, FilmGenreApi, FilmPeopleApi
from services.film import FilmService, get_film_service

# Объект router, в котором регистрируем обработчики
router = APIRouter()

# FastAPI в качестве моделей использует библиотеку pydantic
# https://pydantic-docs.helpmanual.io
# У неё есть встроенные механизмы валидации, сериализации и десериализации
# Также она основана на дата-классах

"""
Модели ответа API
"""

# С помощью декоратора регистрируем обработчик film_details
# На обработку запросов по адресу <some_prefix>/some_id
# Позже подключим роутер к корневому роутеру
# И адрес запроса будет выглядеть так — /api/v1/film/some_id
# В сигнатуре функции указываем тип данных, получаемый из адреса запроса (film_id: str)
# И указываем тип возвращаемого объекта — Film
# @router.get('/{film_id}', response_model=Film)
# async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
#     film = await film_service.get_by_id(film_id)


@router.get('/{film_id}', response_model=FilmApi)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> FilmApi:
    """
        Пример обращений, которые должны обрабатываться API
        #GET /api/v1/film/bf3bd131-b844-4585-9974-6c374cff2371
    """

    film = await film_service.get_by_id(film_id)
    if not film:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessage.FILM_NOT_FOUND)

    # Перекладываем данные из models.Film в Film
    # Обратите внимание, что у модели бизнес-логики есть поле description
    # Которое отсутствует в модели ответа API.
    # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
    # вы бы предоставляли клиентам данные, которые им не нужны
    # и, возможно, данные, которые опасно возвращать

    genre_list = [FilmGenreApi(uuid=genres.get("id"), name=genres.get("name")) for genres in film.genres or []]
    actors_list = [FilmPeopleApi(uuid=actor.get("id"), name=actor.get("name")) for actor in film.actors or []]
    writers_list = [FilmPeopleApi(uuid=writer.get("id"), name=writer.get("name")) for writer in film.writers or []]

    return FilmApi(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating, description=film.description,
                   genre=genre_list, actors=actors_list, writers=writers_list, director=film.director)


@router.get('/')
async def film_list_by_genre(sort: Literal["-imdb_rating", "+imdb_rating"] = "-imdb_rating",
                             filter_genre: UUID = Query(None, alias="filter[genre]"),
                             page_size: int = Query(None, alias="page[size]"),
                             page_number: int = Query(None, alias="page[number]"),
                             film_service: FilmService = Depends(get_film_service)
                             ) -> List[FilmBriefApi]:
    """
        Примеры обращений, которые должны обрабатываться API
        #GET /api/v1/film?sort=-imdb_rating&page[size]=50&page[number]=1
        #GET /api/v1/film?filter[genre]=<uuid:UUID>&sort=-imdb_rating&page[size]=50&page[number]=1
    """

    logging.debug(f"Получили параметры {sort=}-{type(sort)}, {filter_genre=}-{type(filter_genre)},"
                  f" {page_size=}-{type(page_size)}, {page_number=}-{type(page_number)}")
    # Получаем список фильмов
    # Доработать сортировку ort=-imdb_rating
    films = await film_service.get_by_genre_id(filter_genre, sort, page_size, page_number)
    if not films:
        # Если выборка пустая, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ErrorMessage.FILM_NOT_FOUND)
    # Перекладываем данные из models.Film в Film
    films_api = [FilmBriefApi(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating) for film in films]
    return films_api
