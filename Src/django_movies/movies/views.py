import os

from django.shortcuts import render

from movies.models import FilmWork


def index_view(request):
    """
    Главная страница приложения, которая открывается при открытии
    корневого каталога сайта
    """
    return render(
        request,
        "movies/index.html",
        context={
            # Отобразить на странице идентификатор пользователя,
            # от имени которого выполняется приложение. Важно, чтобы
            # это не был идентификатор суперпользователя.
            'uid': os.geteuid(),
            # Передаем для отображения список из первых 200 фильмов
            'movies': FilmWork.objects.all()[:200]
        }
    )
