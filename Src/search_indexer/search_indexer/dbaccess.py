"""
Функции доступа к базе данных онлайн-кинотеатра
"""

import psycopg2


class MovieDB:
    """
    Подключение к базе данных онлайн-кинотеатра
    """

    def __init__(self,
                 *,
                 username: str,
                 password: str,
                 dbname: str,
                 host: str = "127.0.0.1",
                 port: int = 5432):
        """
        Подключиться к базе данных онлайн-кинотеатра
        """
        conn_str = f"dbname={dbname} user={username} password={password} host={host} port={port}"
        self.connection = psycopg2.connect(conn_str, options="-c search_path=content")
        self.connection.readonly = True
        self.cursor = self.connection.cursor()

    def get_data_to_update(self,
                           *,
                           last_update=None,
                           min_size: int = 10):
        """
        Извлекает из базы блок фильмов, время последнего обновления
        которых более позднее, чем last_update. Возвращается min_size
        фильмов с самым ранним временем обновления, превышающим
        порог, но может быть возвращено и больше, если это необходимо,
        чтобы не дробить список фильмов, имеющих в точности одинаковое
        время последнего обновления.

        Параметры
        ---------
        last_update: datetime.datetime, необязателен
            Время последнего обновления поискового индекса. Если не задано,
            то считается что индекс еще не создавался

        min_size: int
            Минимальный размер извлекаемого блока данных. Может быть
            возвращено меньше фильмов, если их всего меньше. Может
            быть возвращено больше фильмов, если несколько последних
            из них имеют одинаковое время поседнего обновления.

        Возвращает
        ----------
        results: list
            Список фильмов, каждый из которых представлен словарем
            со следующими полями:

            *   id
            *   title
            *   description
        """
        if last_update is not None:
            ts = last_update.isoformat()
            # Этот запрос сгенерирован Django. Он возвращает список из
            # 10 фильмов, обновленных ранее всех, но позже, чем
            # last_update.
            # FIXME: Вполне очевидно, что написание таких запросов
            #        вручную - плохая идея. Разумнее было бы, скорее,
            #        взаимодействовать с Django-приложением через API
            query = f'SELECT DISTINCT "film_work"."id", "film_work"."title", "film_work"."description", "film_work"."creation_date", "film_work"."certificate", "film_work"."file_path", "film_work"."rating", "film_work"."type", "film_work"."created_at", "film_work"."updated_at", MAX("person"."updated_at") AS "last_person_updated", MAX("genre"."updated_at") AS "last_genre_updated", GREATEST("film_work"."updated_at", MAX("genre"."updated_at"), MAX("person"."updated_at")) AS "last_updated" FROM "film_work" LEFT OUTER JOIN "person_film_work" ON ("film_work"."id" = "person_film_work"."film_work_id") LEFT OUTER JOIN "person" ON ("person_film_work"."person_id" = "person"."id") LEFT OUTER JOIN "genre_film_work" ON ("film_work"."id" = "genre_film_work"."film_work_id") LEFT OUTER JOIN "genre" ON ("genre_film_work"."genre_id" = "genre"."id") GROUP BY "film_work"."id" HAVING GREATEST("film_work"."updated_at", MAX("genre"."updated_at"), MAX("person"."updated_at")) > \'{ts}\'::timestamptz ORDER BY "last_updated" ASC, "film_work"."id" ASC LIMIT 10'
        else:
            # Такой же запрос, но без фильтрации по времени последнего
            # обновления поискового индекса
            query = 'SELECT DISTINCT "film_work"."id", "film_work"."title", "film_work"."description", "film_work"."creation_date", "film_work"."certificate", "film_work"."file_path", "film_work"."rating", "film_work"."type", "film_work"."created_at", "film_work"."updated_at", MAX("person"."updated_at") AS "last_person_updated", MAX("genre"."updated_at") AS "last_genre_updated", GREATEST("film_work"."updated_at", MAX("genre"."updated_at"), MAX("person"."updated_at")) AS "last_updated" FROM "film_work" LEFT OUTER JOIN "person_film_work" ON ("film_work"."id" = "person_film_work"."film_work_id") LEFT OUTER JOIN "person" ON ("person_film_work"."person_id" = "person"."id") LEFT OUTER JOIN "genre_film_work" ON ("film_work"."id" = "genre_film_work"."film_work_id") LEFT OUTER JOIN "genre" ON ("genre_film_work"."genre_id" = "genre"."id") GROUP BY "film_work"."id" ORDER BY "last_updated" ASC, "film_work"."id" ASC LIMIT 10'
        self.cursor.execute(query)
        if self.cursor.rowcount == 10:
            # Запросить фильмы, время изменения которых совпадает с
            # последним из ранее запрошенных
            for row in self.cursor.fetchall():
                last_ts = row[12].isoformat()
            if last_update is not None:
                ts = last_update.isoformat()
                query = f'SELECT DISTINCT "film_work"."id", "film_work"."title", "film_work"."description", "film_work"."creation_date", "film_work"."certificate", "film_work"."file_path", "film_work"."rating", "film_work"."type", "film_work"."created_at", "film_work"."updated_at", MAX("person"."updated_at") AS "last_person_updated", MAX("genre"."updated_at") AS "last_genre_updated", GREATEST("film_work"."updated_at", MAX("genre"."updated_at"), MAX("person"."updated_at")) AS "last_updated" FROM "film_work" LEFT OUTER JOIN "person_film_work" ON ("film_work"."id" = "person_film_work"."film_work_id") LEFT OUTER JOIN "person" ON ("person_film_work"."person_id" = "person"."id") LEFT OUTER JOIN "genre_film_work" ON ("film_work"."id" = "genre_film_work"."film_work_id") LEFT OUTER JOIN "genre" ON ("genre_film_work"."genre_id" = "genre"."id") GROUP BY "film_work"."id" HAVING (GREATEST("film_work"."updated_at", MAX("genre"."updated_at"), MAX("person"."updated_at")) > \'{ts}\'::timestamptz AND GREATEST("film_work"."updated_at", MAX("genre"."updated_at"), MAX("person"."updated_at")) <= \'{last_ts}\'::timestamptz) ORDER BY "last_updated" ASC, "film_work"."id"'
            else:
                query = f'SELECT DISTINCT "film_work"."id", "film_work"."title", "film_work"."description", "film_work"."creation_date", "film_work"."certificate", "film_work"."file_path", "film_work"."rating", "film_work"."type", "film_work"."created_at", "film_work"."updated_at", MAX("person"."updated_at") AS "last_person_updated", MAX("genre"."updated_at") AS "last_genre_updated", GREATEST("film_work"."updated_at", MAX("genre"."updated_at"), MAX("person"."updated_at")) AS "last_updated" FROM "film_work" LEFT OUTER JOIN "person_film_work" ON ("film_work"."id" = "person_film_work"."film_work_id") LEFT OUTER JOIN "person" ON ("person_film_work"."person_id" = "person"."id") LEFT OUTER JOIN "genre_film_work" ON ("film_work"."id" = "genre_film_work"."film_work_id") LEFT OUTER JOIN "genre" ON ("genre_film_work"."genre_id" = "genre"."id") GROUP BY "film_work"."id" HAVING (GREATEST("film_work"."updated_at", MAX("genre"."updated_at"), MAX("person"."updated_at")) <= \'{last_ts}\'::timestamptz) ORDER BY "last_updated" ASC, "film_work"."id"'
            self.cursor.execute(query)
        results = []
        for row in self.cursor.fetchall():
            result = {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "imdb_rating": row[6],
                "last_updated": row[12].isoformat()
            }
            results.append(result)
        # Дополняем результаты списками актеров, режиссеров и сценаристов,
        # а также жанров
        for res in results:
            # Сначала жанры
            query = f'SELECT "film_work"."id", "genre"."title" FROM "film_work" LEFT OUTER JOIN "genre_film_work" ON ("film_work"."id" = "genre_film_work"."film_work_id") LEFT OUTER JOIN "genre" ON ("genre_film_work"."genre_id" = "genre"."id") WHERE "film_work"."id" = \'{res["id"]}\''
            self.cursor.execute(query)
            res['genre'] = ", ".join(
                [
                    row[1] for row in self.cursor.fetchall()
                ]
            )
            # Теперь съемочная группа
            res["director"] = ""
            res["actor_names"] = ""
            res["writer_names"] = ""
            query = f'SELECT "film_work"."id", "person"."person_name", "person_film_work"."worktype" FROM "film_work" LEFT OUTER JOIN "person_film_work" ON ("film_work"."id" = "person_film_work"."film_work_id") LEFT OUTER JOIN "person" ON ("person_film_work"."person_id" = "person"."id") WHERE "film_work"."id" = \'{res["id"]}\''
            self.cursor.execute(query)
            for row in self.cursor.fetchall():
                if row[2] == "actor":
                    if res["actor_names"]:
                        res["actor_names"] += "; "
                    res["actor_names"] += row[1]
                if row[2] == "director":
                    if res["director"]:
                        res["director"] += "; "
                    res["director"] += row[1]
                if row[2] == "writer":
                    if res["writer_names"]:
                        res["writer_names"] += "; "
                    res["writer_names"] += row[1]
        return results
