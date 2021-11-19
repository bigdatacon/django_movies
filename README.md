Сайт с базой данных фильмов на Django
=====================================

Запуск сервиса
--------------

1.  Создайте каталог ../Postgres. В нем будут файлы образа базы данных.
    Если эти файлы образа у Вас уже есть - скопируйте их в этот каталог.

2.  Соберите docker-контейнеры с помощью команды
    docker-compose build

3.  Запустите сервисы с помощью команды
    docker-compose up
    Она запустит 3 сервиса - Nginx, прослушивающий порт 8000, PostgreSQL,
    прослушивающий порт 5432 и uWsgi/Django, прослушивающий локальный
    UNIX-сокет.

4.  Если Вы не копировали образ базы данных в ../Postgres на шаге 1, то
    сейчас нужно создать базу данных. Подключитесь к контейнеру Postgres
    командой psql --username=postgres --host=127.0.0.1 --port=5432 и
    создайте базу данных командой `CREATE DATABASE movies`. Затем перейдите
    в каталог src/django_movies и введите команду python3 manage.py migrate.
    Эта команда укажет Django соединиться с СУБД и автоматически создать
    все таблицы в соответствии с моделями Django.
