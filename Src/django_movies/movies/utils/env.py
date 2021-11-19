import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent


def load_env():
    """
    Загружает переменные окружения, определяющие используемую
    базу данных, из файла конфигурации
    """
    path = Path(BASE_DIR / ".env")
    content = path.read_text()
    for line in content.split('\n'):
        # Игнорируем пустые строки, содержащие только пробелы
        if not line.strip():
            continue
        # Разбиваем строку на имя и значение по первому
        # встретившемуся знаку равенства
        # Значение может содержать в себе и другие знаки равенства,
        # разбиение идет только по первому
        values = line.split('=', maxsplit=1)
        os.environ[values[0]] = values[1]
