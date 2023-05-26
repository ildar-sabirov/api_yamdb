from django.contrib import admin

from .models import Category, Genre, Title, TitleGenres, User

admin.site.register(User)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'year', 'description', 'category')


admin.site.register(TitleGenres)  # временно для тестов - удалить!

admin.site.register(Category)

admin.site.register(Genre)
