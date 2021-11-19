"""
Индексировать содержимое базы в ElasticSearch

Параметры командной строки
--------------------------
--restart
    Очистить текущий индекс и начать сначала. Если эта опция не
    указана, индексирование будет возобновлено с момента, на котором
    оно было прервано.
"""

import datetime
import json
import logging
import os
import time
from functools import wraps

import requests
from django.core.management.base import BaseCommand
from django.db.utils import DatabaseError
from requests.exceptions import RequestException

from movies.models import FilmWork
from movies.utils.state import JsonFileStorage, State

CONFIG = {}


def backoff(start_sleep_time=0.1,
            factor=2,
            border_sleep_time=10,
            *,
            logger=None):
    """
    Функция для повторного выполнения функции через некоторое время,
    если возникла ошибка. Использует наивный экспоненциальный рост
    времени повтора (factor) до граничного времени ожидания
    (border_sleep_time)

    Формула:
    t = start_sleep_time * 2^(n) if t < border_sleep_time
    t = border_sleep_time if t >= border_sleep_time

    Параметры
    ---------
    start_sleep_time: float
        начальное время повтора

    factor: float
        во сколько раз нужно увеличить время ожидания

    border_sleep_time: float
        граничное время ожидания

    logger: logging.Logger
        Объект логгера, который (если он не None) будет использоваться
        для записи информации о неудачных попытках подключения

    Возвращает
    ----------
    result: any
        результат выполнения функции
    """
    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            while True:
                try:
                    result = func(*args, **kwargs)
                    return result
                except (RequestException, DatabaseError) as e:
                    # Повторяем попытку если исключение возникло в
                    # базе данных (DatabaseError) или при установлении
                    # соединения в requests
                    time.sleep(sleep_time)
                    sleep_time *= factor
                    sleep_time = min(sleep_time, border_sleep_time)
                    if logger is not None:
                        logger.warning("Перехвачено исключение: '{}', повторяем попытку позже...".format(e))
        return inner
    return func_wrapper


@backoff(logger=logging.getLogger("warning"))
def create_search_schema():
    """
    Записывает в поисковый движок схему документа
    """
    resp = requests.put(
        "http://{}/movies".format(CONFIG['elasticsearchServer']),
        json=CONFIG['indexScheme']
    )
    return resp.status_code == 200


@backoff(logger=logging.getLogger("warning"))
def transfer_datablock(state):
    """
    Считать из базы данных несколько первых, обновленных позже
    последнего обновления поискового индекса, и перенести
    последние сведения о них в индекс.

    Логика устроена так, что берется 10 записей, а потом все
    последующие, время обновления которых совпадает с временем
    обновления десятой. Это позволяет не пропускать записи,
    если сразу много записей обновлены одновременно (а это
    случается, так как при обновлении актера обновляются все
    его фильмы). При следующем вызове обрабатываются все записи,
    время обновления которых строго больше, чем время обновления
    последней уже обработанной.

    Параметры
    ---------
    state: State
        Состояние передачи, включает время обновления последнего
        фильма, информация о котором была успешно обновлена.

    Возвращает
    ----------
    total_objects: int
        Общее число записей которые требовалось обновить. Ноль
        означает, что индекс в полностью актуальном состоянии.

    successful_objects: int
        Количество записей, которые были успешно обновлены.

    failed_objects: int
        Количество записей, обновившихся с ошибкой
    """
    # Получить время последнего обновления поискового индекса.
    # Обновлять будем только информацию о фильмах, обновленных
    # после этого. Сортируем по времени обновления, чтобы
    # переиндексировать в порядке, соответствующем порядку
    # изменений в базе. Но при этом также сортируем по ID,
    # чтобы порядок был стабильным. Переменная films_q - это
    # запрос к базе, а films - возвращенный им список
    last_update = state.get_state("last_update")
    if last_update is None:
        films_q = FilmWork.annotate_last_updates().order_by(
            'last_updated', 'id'
        )
    else:
        last_update = datetime.datetime.fromisoformat(last_update)
        films_q = FilmWork.annotate_last_updates().filter(
            last_updated__gt=last_update
        ).order_by('last_updated', 'id')
    if films_q.count() <= 10:
        films = list(films_q)
    else:
        films = list(films_q.filter(last_updated__lte=films_q[10].last_updated))
    total_objects = len(films)
    successful_objects = 0
    failed_objects = 0
    if not total_objects:
        return 0, 0, 0
    # Запоминаем текущее время - после обновления поискового индекса
    # запишем его как время последнего обновления
    last_update = films[-1].last_updated.isoformat()
    # Проходимся по фильмам и запоминаем каждый в поисковый индекс
    bulk = []
    for film in films:
        bulk.append(
            {"index": {"_index": "movies", "_id": str(film.id)}}
        )
        bulk.append(
            film.to_elasticsearch()
        )
    resp = requests.post(
        "http://{}/_bulk".format(CONFIG['elasticsearchServer']),
        data="\n".join(json.dumps(item) for item in bulk) + "\n",
        headers={'content-type':'application/x-ndjson'}
    )
    resp_data = resp.json()
    if resp_data.get("errors", False):
        print(resp_data["errors"])
    else:
        successful_objects = total_objects
    resp = requests.get(
        "http://{}/_refresh".format(CONFIG['elasticsearchServer'])
    )
    state.set_state("last_update", last_update)
    return total_objects, successful_objects, failed_objects


def read_config(filename: str):
    """
    Считать файл конфигурации. Этот файл должен быть в JSON формате
    и содержать 2 поля: строку "elasticsearchServer" и словарь
    "indexScheme".
    """
    with open(filename) as fd:
        conf = json.load(fd)
    return conf


class Command(BaseCommand):
    """
    Команда для индексирования содержимого базы данных в ElasticSearch
    """

    def add_arguments(self, parser):
        """
        Заполнить список допустимых параметров командной строки
        """
        parser.add_argument(
            "--restart",
            action="store_const",
            const=True,
            default=False,
            help="Очистить текущий индекс и начать сначала"
        )
        parser.add_argument(
            "--config-file",
            action="store",
            type=str,
            default="/etc/index_search_config.json",
            help="Считать опции для настройки ElasticSearch из этого файла"
        )

    def handle(self, *args, **options):
        """Выполнить команду"""
        state = State(
            JsonFileStorage(
                os.path.join(
                    os.getenv("HOME"),
                    ".django_movies",
                    "search_index_state.json"
                )
            )
        )
        global CONFIG
        CONFIG = read_config(options.get("config_file"))
        if options.get("restart", False):
            state.reset_state()
        if not state.get_state("schema_created"):
            if create_search_schema():
                state.set_state("schema_created", True)
                self.stderr.write(
                    self.style.SUCCESS("Схема создана")
                )
            else:
                self.stderr.write(
                    self.style.ERROR("Создать схему не удалось")
                )
        while True:
            time.sleep(5)
            (total_objects, successful_objects, failed_objects) = transfer_datablock(state)
            if not total_objects:
                self.stderr.write(
                    self.style.SUCCESS("Обновление поискового индекса завершено")
                )
                return
            elif failed_objects:
                self.stderr.write(
                    self.style.ERROR("Удачно обновлены {} из {} записей".format(successful_objects, total_objects))
                )
            else:
                self.stderr.write(
                    self.style.SUCCESS("Удачно обновлены все {} записей".format(total_objects))
                )
