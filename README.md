# Ссылка на репозиторий
https://github.com/johanijbabaj/Async_API_sprint_1/

# Настройка

## Настройка Postgres
- Настройка переменных окружения. Создайте файл db.env, и укажите в неё значения: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD (в качестве примера можно взять файл db.env.example)
- Добавление файлов БД. Создайте в корне проекта папку pgdata, и поместите туда файлы БД (можно использовать вот эти https://drive.google.com/file/d/1INh4uMXfcJfNXhisvVBWrJ_kDNxFoziT/view?usp=sharing)
- 
## Настройка Django
- Настройка переменных окружения. Создайте файл movies_admin/.env, и укажите в неё значения: SECRET_KEY, ALLOWED_HOSTS, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT (в качестве примера можно взять файл movies_admin/.env.example)

## Настройка Elastic
- Настройка переменных окружения. Создайте файл es.env, и укажите в неё значения: discovery.type (в качестве примера можно взять файл es.env.example)

## Настройка ETL
- Создание конфигурации. В конфигурационном файле postgres_to_es/settings/settings.json (файл нужно создать, в качестве примера можно взять файл postgres_to_es/settings/settings.json.example) необходимо указать параметры подключения к Postgres и Elasticsearch.

## Настройка FastAPI
- Настройка переменных окружения. Создайте файл fa.env, и укажите в нем значения: PROJECT_NAME, REDIS_HOST, REDIS_PORT, REDIS_AUTH, ELASTIC_HOST, ELASTIC_PORT (в качестве примера можно взять файл fa.env.example)

# Взаимодействие
- Доступ к документации FastAPI осуществляется через http://localhost:8000/api/openapi
- Доступ к админке Django осуществляется через http://localhost/admin/ (user admin, password 123456)

# Проектная работа 4 спринта

**Важное сообщение для тимлида:** для ускорения проверки проекта укажите ссылку на приватный репозиторий с командной работой в файле readme и отправьте свежее приглашение на аккаунт [BlueDeep](https://github.com/BigDeepBlue).

В папке **tasks** ваша команда найдёт задачи, которые необходимо выполнить в первом спринте второго модуля.  Обратите внимание на задачи **00_create_repo** и **01_create_basis**. Они расцениваются как блокирующие для командной работы, поэтому их необходимо выполнить как можно раньше.

Мы оценили задачи в стори поинтах, значения которых брались из [последовательности Фибоначчи](https://ru.wikipedia.org/wiki/Числа_Фибоначчи) (1,2,3,5,8,…).

Вы можете разбить имеющиеся задачи на более маленькие, например, распределять между участниками команды не большие куски задания, а маленькие подзадачи. В таком случае не забудьте зафиксировать изменения в issues в репозитории.

**От каждого разработчика ожидается выполнение минимум 40% от общего числа стори поинтов в спринте.**