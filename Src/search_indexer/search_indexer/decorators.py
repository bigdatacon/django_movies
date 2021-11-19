"""
Декораторы для сервиса поисковой индексации онлайн-кинотеатра
"""

from functools import wraps
from time import sleep

from psycopg2 import DatabaseError
from requests.exceptions import RequestException


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
                except (RequestException, DatabaseError) as ex:
                    # Повторяем попытку если исключение возникло в
                    # базе данных или при установлении соединения в
                    # requests
                    sleep(sleep_time)
                    sleep_time *= factor
                    sleep_time = min(sleep_time, border_sleep_time)
                    if logger is not None:
                        logger.warning(f"Перехвачено исключение: {ex}")
                        logger.warning("повторяем попытку позже...")
        return inner
    return func_wrapper
