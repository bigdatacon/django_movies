# Generated by Django 3.2.6 on 2021-09-07 11:54

import datetime

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0004_auto_20210907_1144'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='filmwork',
            options={'verbose_name': 'Кинопроизведение', 'verbose_name_plural': 'Кинопроизведения'},
        ),
        migrations.AlterModelOptions(
            name='genre',
            options={'verbose_name': 'Жанр', 'verbose_name_plural': 'Жанры'},
        ),
        migrations.AlterModelOptions(
            name='genrefilmwork',
            options={'verbose_name': 'Жанр кинопроизведения', 'verbose_name_plural': 'Жанры кинопроизведения'},
        ),
        migrations.AlterModelOptions(
            name='person',
            options={'verbose_name': 'Персона', 'verbose_name_plural': 'Персоны'},
        ),
        migrations.AlterModelOptions(
            name='personfilmwork',
            options={'verbose_name': 'Участник кинопроизведения', 'verbose_name_plural': 'Участники кинопроизведения'},
        ),
        migrations.AlterField(
            model_name='filmwork',
            name='certificate',
            field=models.TextField(blank=True, verbose_name='Сертификат'),
        ),
        migrations.AlterField(
            model_name='filmwork',
            name='creation_date',
            field=models.DateField(blank=True, verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='filmwork',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='filmwork',
            name='file_path',
            field=models.FileField(upload_to='film_works/', verbose_name='Путь к файлу'),
        ),
        migrations.AlterField(
            model_name='filmwork',
            name='genres',
            field=models.ManyToManyField(through='movies.GenreFilmWork', to='movies.Genre', verbose_name='Жанры'),
        ),
        migrations.AlterField(
            model_name='filmwork',
            name='person',
            field=models.ManyToManyField(through='movies.PersonFilmWork', to='movies.Person', verbose_name='Персоны'),
        ),
        migrations.AlterField(
            model_name='filmwork',
            name='rating',
            field=models.FloatField(blank=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Рейтинг'),
        ),
        migrations.AlterField(
            model_name='filmwork',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='filmwork',
            name='type',
            field=models.CharField(choices=[('movie', 'movie'), ('tv_show', 'TV Show')], max_length=20, verbose_name='Тип'),
        ),
        migrations.AlterField(
            model_name='genrefilmwork',
            name='created_at',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 9, 7, 11, 54, 36, 17072), verbose_name='Дата обращения'),
        ),
        migrations.AlterField(
            model_name='personfilmwork',
            name='created_at',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 9, 7, 11, 54, 36, 17297), verbose_name='Дата обращения'),
        ),
    ]
