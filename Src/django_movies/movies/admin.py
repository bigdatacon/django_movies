from django.contrib import admin

from .models import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork
    extra = 0


class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork
    extra = 0


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'creation_date', 'rating')
    fields = (
        'title', 'type', 'description', 'creation_date', 'certificate',
        'file_path', 'rating'
    )

    inlines = [PersonFilmWorkInline, GenreFilmWorkInline]

    list_filter = ('type', 'genres')

    search_fields = ('title', 'description', 'id')

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')
    fields = (
        'title', 'description',
    )

    search_fields = ('title', 'description', 'id')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('person_name', 'gender')
    fields = (
        'person_name', 'gender',
    )

    list_filter = ('gender',)

    search_fields = ('person_name', 'id')

