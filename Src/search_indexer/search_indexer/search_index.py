"""
Функции индексирования кинопроизведений в ElasticSearch
"""

import datetime
import json
import logging
import time

import requests

from search_indexer.dbaccess import MovieDB
from search_indexer.decorators import backoff
from search_indexer.state import JsonFileStorage, State

logger = logging.getLogger()


@backoff(logger=logger)
def create_search_schema(es_url, scheme):
    """
    Записывает в поисковый движок схему документа

    Параметры
    ---------
    es_url: str
        Строка с URL поискового движка

    scheme: dict
        Схема поискового индекса
    """
    resp = requests.put(
        "http://{}/movies".format(es_url), json=scheme
    )
    if resp.status_code != 200:
        logger.warning(f"Ошибка создания поискового индекса: {resp.json()}")
    return resp.status_code == 200


@backoff(logger=logger)
def transfer_datablock(es_url, db, state):
    """
    Берет из базы данных набор недавно обновленных фильмов и
    переиндексирует их в поисковом движке

    Параметры
    ---------
    es_url: str
        URL для подключения к ElasticSearch

    db: MovieDB
        Подключение к базе данных

    state: State
        Состояние передачи данных от базы к ElasticSearch

    Возвращает
    ----------
    total_objects: int
        Количество объектов, которые нужно было обновить

    successful_objects: int
        Количество объектов, которые были успешно обновлены
    """
    last_update = state.get_state("last_update")
    if last_update is not None:
        last_update = datetime.datetime.fromisoformat(last_update)
    data = db.get_data_to_update(last_update=last_update)
    if not data:
        return 0, 0
    last_update = data[-1]["last_updated"]
    bulk = []
    total_objects = len(data)
    successful_objects = 0
    for item in data:
        # Это поле нужно, чтобы запомнить его значение в state, но
        # не должно попасть в поисковый индекс
        item.pop('last_updated')
        bulk.append(
            {"index": {"_index": "movies", "_id": str(item["id"])}}
        )
        bulk.append(item)
    resp = requests.post(
        f"http://{es_url}/_bulk",
        data="\n".join([json.dumps(item) for item in bulk]) + "\n",
        headers={'content-type': 'application/x-ndjson'}
    )
    resp_data = resp.json()
    if resp_data.get("errors", False):
        logger.warning(f"Индексирование блока данных вызвало ошибку: {resp_data}")
    else:
        successful_objects = total_objects
    resp = requests.get(f"http://{es_url}/_refresh")
    state.set_state("last_update", last_update)
    return total_objects, successful_objects


@backoff(logger=logger)
def connect_db(db_config):
    """
    Создать подключение к базе данных системы

    Параметры
    ---------
    db_config: dict
        Словарь с параметрами подключения к базе данных

    Возвращает
    ----------
    db: MovieDB
        Подключение к базе данных
    """
    return MovieDB(
        username=db_config.get("username"),
        password=db_config.get("password"),
        dbname=db_config.get("dbname"),
        host=db_config.get("host", "127.0.0.1"),
        port=db_config.get("port", 5432)
    )


def run_search_index(config: dict, restart: bool = False):
    """
    Переиндексирует содержимое базы данных в поисковом движке
    """
    db_config = config["database"]
    es_config = config["elasticsearchServer"]
    scheme = config["indexScheme"]
    state_file = config["stateFile"]
    logger.info("Запущено обновление поискового индекса")
    state = State(JsonFileStorage(state_file))
    if restart:
        state.reset_state()
    if not state.get_state("schema_created"):
        if create_search_schema(es_config, scheme):
            state.set_state("schema_created", True)
            logger.info("Схема поискового индекса создана")
        else:
            logger.error("Создать схему поискового индекса не удалось")
    db = connect_db(db_config)
    while True:
        time.sleep(5)
        total_objects, successful_objects = transfer_datablock(es_config, db, state)
        if not total_objects:
            logger.info("Обновление поискового индекса завершено")
            return
        elif successful_objects != total_objects:
            logger.warning(f"Удачно обновлены {successful_objects} из {total_objects} записей")
        else:
            logger.warning(f"Удачно обновлены все {total_objects} записей")
