from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.timezone import now


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name='Категория')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Ссылка')

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name='Жанр')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Ссылка')

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField(max_length=256, verbose_name='Произведение')
    year = models.PositiveIntegerField(validators=[MaxValueValidator(now)])
    description = models.CharField(blank=True, max_length=2000)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles',
    )
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenres',
        through_fields=('title', 'genre'),
        related_name='titles',
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class TitleGenres(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title.__str__()}_{self.genre.__str__()}'
