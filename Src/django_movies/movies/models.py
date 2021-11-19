import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Gender(models.TextChoices):
    MALE = 'male', _('мужской')
    FEMALE = 'female', _('женский')


class TimeStampedMixin:
    """
    Миксин-класс для всех моделей, содержащих поля created_at и
    updated_at. Включать сами поля в класс не производный от
    models.Model оказалось плохой идеей, так как они не обрабатываются
    командой makemigrations/migrate, поэтому поля в каждом
    классе объявлены отдельно - а здесь будут общие функции для
    работы с ними и т.п.
    """
    pass


class Genre(models.Model, TimeStampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_('title'), max_length=255)
    # blank=True делает поле необязательным для заполнения.
    description = models.TextField(_('description'), blank=True)
    # Время последнего изменения записи. Здесь мы дублируем содержимое
    # TimeStampedMixin вместо подключения миксина, так как при
    # добавлении миксина не генерируется файл миграции базы данных.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Жанр')
        verbose_name_plural = _('Жанры')
        # Ваши таблицы находятся в нестандартной схеме. Это тоже нужно указать в классе модели
        db_table = "genre"

    def __str__(self):
        return f"{self.title}"


class Person(models.Model, TimeStampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person_name = models.CharField(_('имя'), max_length=50)
    gender = models.TextField(_('пол'), choices=Gender.choices, null=True)
    # Время последнего изменения записи. Здесь мы дублируем содержимое
    # TimeStampedMixin вместо подключения миксина, так как при
    # добавлении миксина не генерируется файл миграции базы данных.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Персона')
        verbose_name_plural = _('Персоны')
        db_table = "person"

    def __str__(self):
        return f"{self.person_name}"


class GenreFilmWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    film_work = models.ForeignKey('FilmWork', on_delete=models.CASCADE, default=None)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE, default=None)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, verbose_name=_('Дата обращения'))

    class Meta:
        db_table = "genre_film_work"
        verbose_name = _('Жанр кинопроизведения')
        verbose_name_plural = _('Жанры кинопроизведения')


class PersonFilmWorkType(models.TextChoices):
    ACTOR = 'actor', _('actor'),
    DIRECTOR = 'director', _('director'),
    WRITER = 'writer', _('writer'),
    OTHER = 'other', _('other')


class PersonFilmWork(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    film_work = models.ForeignKey('FilmWork', on_delete=models.CASCADE, default=None)
    person = models.ForeignKey('Person', on_delete=models.CASCADE, default=None)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, verbose_name=_('Дата обращения'))
    worktype = models.CharField(_('Тип участия'), max_length=30, choices=PersonFilmWorkType.choices, default=PersonFilmWorkType.OTHER)

    class Meta:
        db_table = "person_film_work"
        verbose_name = _('Участник кинопроизведения')
        verbose_name_plural = _('Участники кинопроизведения')


class FilmWorkType(models.TextChoices):
    MOVIE = 'movie', _('movie')
    TV_SHOW = 'tv_show', _('TV Show')


class FilmWork(models.Model, TimeStampedMixin):
    """Фильм или телепередача"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    title = models.CharField(_('Название'), max_length=255)
    description = models.TextField(_('Описание'), blank=True)
    creation_date = models.DateField(_('Дата создания'), blank=True)
    certificate = models.TextField(_('Сертификат'), blank=True)
    file_path = models.FileField(_('Путь к файлу'), upload_to='film_works/')
    rating = models.FloatField(
        _('Рейтинг'),
        validators=[MinValueValidator(0)],
        blank=True
    )
    # Является ли объект фильмом или передачей
    type = models.CharField(
        _('Тип'),
        max_length=20,
        choices=FilmWorkType.choices
    )
    # Список жанров фильма
    genres = models.ManyToManyField(
        Genre,
        through='GenreFilmWork',
        verbose_name=_('Жанры')
    )
    # Люди, участвовавшие в создании фильма: актеры, режиссеры и сценаристы
    persons = models.ManyToManyField(
        Person,
        through='PersonFilmWork',
        verbose_name=_('Персоны')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Кинопроизведение')
        verbose_name_plural = _('Кинопроизведения')
        db_table = "film_work"

    @property
    def directors(self):
        """Список режиссеров фильма в виде объекта QuerySet"""
        persons = set(
            self.personfilmwork_set.filter(
                worktype=PersonFilmWorkType.DIRECTOR
            ).values_list('person_id', flat=True)
        )
        return Person.objects.filter(id__in=persons)

    @property
    def actors(self):
        """Список актеров фильма в виде объекта QuerySet"""
        persons = set(
            self.personfilmwork_set.filter(
                worktype=PersonFilmWorkType.ACTOR
            ).values_list('person_id', flat=True)
        )
        return Person.objects.filter(id__in=persons)

    @property
    def writers(self):
        """Список сценаристов фильма в виде объекта QuerySet"""
        persons = set(
            self.personfilmwork_set.filter(
                worktype=PersonFilmWorkType.WRITER
            ).values_list('person_id', flat=True)
        )
        return Person.objects.filter(id__in=persons)

    def to_elasticsearch(self):
        """
        Возвращает JSON-представление фильма, которое можно загрузить
        в ElasticSearch
        """
        director = self.directors.first()
        obj = {
            "id": str(self.id),
            "imdb_rating": str(self.rating),
            "genre": str(self.genres.first().title),
            "title": self.title,
            "description": self.description,
            "director": str(director.person_name) if director is not None else "",
            "actor_names": "; ".join([str(actor.person_name) for actor in self.actors]),
            "writer_names": "; ".join([str(writer.person_name) for writer in self.writers])
        }
        return obj

    @staticmethod
    def annotate_last_updates():
        """
        Возвращает запрос на список всех объектов типа Filmwork
        с добавленным полем last_updated, хранящим наиболее позднее
        время последнего изменения фильма, его жанра или любого
        из участников работы над фильмом - актера, режиссера или
        сценариста. В общем, добавляет поле последнего изменения
        фильма, включая его данные из других таблиц. Возвращается
        запрос FilmWork.objects в котором дополнительно доступно
        поле last_updated, по которому запрос можно будет отфильтровать
        и отсортировать.
        """
        return FilmWork.objects.annotate(
            last_person_updated=models.Max('persons__updated_at')
        ).annotate(
            last_genre_updated=models.Max('genres__updated_at')
        ).annotate(
            last_updated=models.functions.Greatest(
                models.F('updated_at'),
                models.F('last_genre_updated'),
                models.F('last_person_updated')
            )
        ).distinct()
