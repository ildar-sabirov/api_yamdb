from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

from django.db import models
from django.utils.timezone import now


OUTPUT_LENGTH = 30

ROLE_CHOICES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор')
)


class User(AbstractUser):
    """
    Модель пользователя платформы.
    Используется в системе аутентификации Django.
    """
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False
    )
    email = models.EmailField(
        max_length=250,
        unique=True,
        blank=False
    )
    first_name = models.CharField(
        max_length=100,
        blank=True
    )
    last_name = models.CharField(
        max_length=100,
        blank=True
    )
    bio = models.TextField(
        blank=True
    )
    role = models.CharField(
        max_length=15,
        choices=ROLE_CHOICES,
        default='user'
    )

    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Category(models.Model):
    """
    Модель категории произведения.
    Используется в модели Произведения.
    описаны 2 поля: название категории и уникальный слаг для адресной строки
    """
    name = models.CharField(
        max_length=256,
        verbose_name='Категория',
        db_index=True
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Ссылка'
    )

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    """
    Модель жанра произведения.
    Используется в модели Произведения.
    описаны 2 поля: название категории и уникальный слаг для адресной строки
    """
    name = models.CharField(
        max_length=256,
        verbose_name='Жанр',
        db_index=True
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Ссылка'
    )

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """
    Модель произведения.
    Содержит данные о названии произведения и годе публикации.
    Опциональные поля: описание, категория и жанр.
    Категория у произведения может быть только одна, а жанров несколько.
    """
    name = models.CharField(
        max_length=256,
        verbose_name='Название произведения',
    )
    year = models.PositiveIntegerField(
        validators=[
            MaxValueValidator(
                now().year, message='Год издания не может быть больше текущего'
            )
        ],
        verbose_name='Год издания',
    )
    description = models.TextField(blank=True, verbose_name='Описание')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenres',
        through_fields=('title', 'genre'),
        related_name='titles',
        verbose_name='Жанр',
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class TitleGenres(models.Model):
    """Модель для связи многие ко многим Произведения-Жанры."""
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'genre'],
                name='unique_title_genre'
            ),
        ]

    def __str__(self):
        return f'{self.title.__str__()}_{self.genre.__str__()}'


class ReviewCommentModel(models.Model):
    text = models.TextField("Текст")
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField(
        "Дата добавления",
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        abstract = True
        ordering = ("-pub_date",)

    def __str__(self):
        return self.text[OUTPUT_LENGTH]


class Review(ReviewCommentModel):
    title = models.ForeignKey(
        Title, verbose_name="Произведение", on_delete=models.CASCADE
    )
    score = models.SmallIntegerField(
        "Оценка произведения",
        validators=[
            MinValueValidator(
                1, message="Оценка должна быть больше или равна 1"
            ),
            MaxValueValidator(
                10, message="Оценка должна быть меньше или равна 10"
            ),
        ],
        default=1,
    )

    class Meta(ReviewCommentModel.Meta):
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        default_related_name = "reviews"
        constraints = [
            models.UniqueConstraint(
                fields=("title", "author"), name="unique_review"
            ),
        ]


class Comment(ReviewCommentModel):
    review = models.ForeignKey(
        Review, verbose_name="Отзыв", on_delete=models.CASCADE
    )

    class Meta(ReviewCommentModel.Meta):
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        default_related_name = "comments"
