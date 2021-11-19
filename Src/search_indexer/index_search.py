#! /usr/bin/env python3

"""
Сервис для индексирования содержимого базы в поисковом движке
"""

from argparse import ArgumentParser

import json
import sys
import time

from search_indexer import run_search_index


def read_config(filename: str):
    """
    Считывает настройки поискового индекса из файла filename.
    Файл должен быть в JSON формате и содержать следующие поля:

    *   "elasticsearchServer"
        Строка вида "IP:port" с адресом сервера ElasticSearch

    *   "indexScheme"
        Схема индекса. Является сложным объектом-словарем, который
        будет как есть передан ElasticSearch

    *   "database"
        Словарь из пяти полей (dbname, username, password, host, port),
        задающих подключение к базе данных с исходной информацией

    *   "stateFile"
        Имя файла для сохранения состояния сервиса
    """
    fd = open(filename, "rt")
    conf = json.load(fd)
    fd.close()
    return conf


if __name__ == "__main__":
    parser = ArgumentParser(add_help=True)
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
    parser.add_argument(
        "--timeout",
        action="store",
        type=int,
        default=None,
        help="Выполнять индексирование в цикле через этот промежуток времени"
    )
    args = parser.parse_args()
    while True:
        config = read_config(args.config_file)
        run_search_index(config, restart=args.restart)
        if args.timeout:
            time.sleep(args.timeout)
            continue
        else:
            sys.exit(0)
