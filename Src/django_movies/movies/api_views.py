"""
API-функции приложения Movies
-----------------------------

Устроены аналогично контроллерам, но возвращают не HTML
а JSON содержимое для отображения мобильными приложениями
или клиентскими фреймворками подобными Vue JS
"""

import math

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import Http404, JsonResponse

from movies.models import FilmWork, PersonFilmWorkType


def _annotate_persons(qs):
    """
    Заранее подгрузить из базы списки актеров, режиссеров и сценаристов
    для всех фильмов в QuerySet
    """
    return qs.annotate(
        actors=ArrayAgg(
            'personfilmwork__person__person_name',
            filter=Q(personfilmwork__worktype=PersonFilmWorkType.ACTOR)
        )
    ).annotate(
        directors=ArrayAgg(
            'personfilmwork__person__person_name',
            filter=Q(personfilmwork__worktype=PersonFilmWorkType.DIRECTOR)
        )
    ).annotate(
        writers=ArrayAgg(
            'personfilmwork__person__person_name',
            filter=Q(personfilmwork__worktype=PersonFilmWorkType.WRITER)
        )
    ).annotate(
        genre_names=ArrayAgg(
            'genres__title', distinct=True
        )
    )


def _convert_result(filmwork):
    """
    Преобразовать Django-объект фильма в словарь с информацией о фильме,
    который можно будет затем сериализовать в JSON
    """
    return {
        'id': filmwork.id,
        'title': filmwork.title,
        'description': filmwork.description,
        'creation_date': str(filmwork.creation_date),
        'rating': filmwork.rating,
        'type': filmwork.type,
        'genres': filmwork.genre_names,
        'actors': filmwork.actors,
        'directors': filmwork.directors,
        'writers': filmwork.writers
    }


def _convert_results(filmworks):
    """
    Преобразовать извлеченный из базы данных набор фильмов в список
    словарей с информацией о фильмах, который можно будет сериализовать
    в JSON
    """
    return [_convert_result(film) for film in filmworks]


def _convert_movies_page(page_number):
    """
    Выбирает фильмы, составляющие определенную страницу в списке
    всех фильмов по 50 на страницу (т.е. для page_number = 1 будет
    список из первых 50 фильмов по алфавиту, для page_number = 2
    фильмы с 50 по 100 и т.п.). Возвращает объект для сериализации
    в JSON, содержащий информацию об этих фильмах, а также об
    общем количестве фильмов, следующей и предыдущей странице.
    """
    page_size = 50
    filmworks = FilmWork.objects.order_by('title').all()
    film_count = filmworks.count()
    page_count = math.ceil(film_count / page_size)
    obj = {
        'count': film_count,
        'total_pages': page_count,
        'prev': page_number - 1 if page_number > 1 else None,
        'next': page_number + 1 if page_number < page_count else None,
        'results': _convert_results(
            _annotate_persons(
                filmworks[
                    page_number * page_size - page_size:page_number * page_size
                ]
            )
        )
    }
    return obj


def get_movies(request):
    """
    Вернуть список фильмов, разбитый на страницы по 50 фильмов.

    Параметры
    ---------
    request: HttpRequest
        Запрос HTTP GET, который может содержать параметр page,
        содержащий номер страницы списка. По умолчанию этот номер
        равен 1.

    Возвращает
    ----------
    response: JsonResponse
        HTTP-ответ с данными в формате JSON. Возвращаемый блок данных
        содержит вседения о 50 фильмах, образующих в списке страницу
        с нужным номером (списки сортируются по алфавиту).
        Ответ является JSON-объектом со следующими полями:

        *   count
            Общее количество фильмов в базе данных системы

        *   total_pages
            Общее количество страниц, на которые разбита выдача

        *   prev
            Номер предыдущей страницы или null, если это первая

        *   next
            Номер следующей страницы или null, если это последняя

        *   result
            Содержимое страницы - массив из 50 элементов каждый
            из которых содержит информацию о фильме в формате,
            идентичном формату данных возвращаемых get_movie
    """
    page_number = int(request.GET.get('page', 1))
    obj = _convert_movies_page(page_number)
    return JsonResponse(obj)


def get_movie(request, movie_id):
    """
    Вернуть информацию о фильме с заданным идентификатором

    Параметры
    ---------
    movie_id: str
        Строка с UUID фильма

    Возвращает
    ----------
    response: JsonResponse
        HTTP-ответ с данными о фильме в формате JSON.
        Содержит следующие поля:

        *   id
            UUID-идентификатор фильма (совпадает с movie_id)

        *   title
            Название фильма, строка

        *   description
            Описание фильма, строка, может быть пустой

        *   creation_date
            Дата создания фильма

        *   rating
            Рейтинг фильма

        *   type
            Тип объекта - определяет, является ли объект фильмом
            или, например, его анонсом в новостях

        *   genres
            Список строк - жанров фильма

        *   actors
            Список имен актеров

        *   directors
            Список имен режиссеров

        *   writers
            Список имен сценаристов
    """
    # Здесь мы не можем использовать get_object_or_404, так как нам
    # нужен qureyset для аннотирования.
    # И не можем использовать get_list_or_404, так как этот метод
    # почему-то возвращает список, а не QuerySet.
    filmworks = FilmWork.objects.filter(id=movie_id)
    if not filmworks.exists():
        raise Http404("Фильм с таким идентификтором не найден")
    obj = _convert_result(_annotate_persons(filmworks).first())
    return JsonResponse(obj)
