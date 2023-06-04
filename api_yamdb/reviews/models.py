from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.timezone import now

from .validators import validate_username

OUTPUT_LENGTH = 30
NAME_LENGTH = 256
SLUG_LENGTH = 50
USERNAME_LENGTH = 150
EMAIL_LENGTH = 254
FIRST_NAME_LENGTH = 150
LAST_NAME_LENGTH = 150
WRONG_YEAR_MESSAGE = 'Год издания не может быть больше текущего'
ROLE_ADMIN = 'admin'
ROLE_MODERATOR = 'moderator'
ROLE_USER = 'user'

ROLE_CHOICES = (
    (ROLE_USER, 'Пользователь'),
    (ROLE_MODERATOR, 'Модератор'),
    (ROLE_ADMIN, 'Администратор')
)


def current_year():
    return now().year


class User(AbstractUser):
    """
    Модель пользователя платформы.
    """
    username = models.CharField(
        max_length=USERNAME_LENGTH,
        unique=True,
        blank=False,
        verbose_name='Имя пользователя',
        validators=[validate_username]
    )
    email = models.EmailField(
        max_length=EMAIL_LENGTH,
        unique=True,
        blank=False,
        verbose_name='Email',
    )
    first_name = models.CharField(
        max_length=FIRST_NAME_LENGTH,
        blank=True,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=LAST_NAME_LENGTH,
        blank=True,
        verbose_name='Фамилия',
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография'
    )
    role = models.CharField(
        max_length=max(len(en) for en, ru in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=ROLE_USER,
        verbose_name='Роль'
    )

    USERNAME_FIELD = 'username'

    @property
    def is_admin(self):
        return self.role == ROLE_ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == ROLE_MODERATOR

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class NameSlug(models.Model):
    """Модель определения названия объекта и имени страницы.
    Используется в моделях Жанр и Категория.
    описаны 2 поля: название имя страницы. Настроена сортировка по имени."""
    name = models.CharField(
        max_length=NAME_LENGTH,
        verbose_name='Название',
        db_index=True
    )
    slug = models.SlugField(
        max_length=SLUG_LENGTH,
        unique=True,
        verbose_name='Имя страницы'
    )

    def __str__(self):
        return f'{self.slug[:OUTPUT_LENGTH]} {type(self)}'

    class Meta:
        abstract = True
        ordering = ('name',)


class Category(NameSlug):
    """
    Модель категории произведения.
    Используется в модели Произведения.
    описаны 2 поля: название категории и уникальный слаг для адресной строки
    """
    class Meta(NameSlug.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(NameSlug):
    """
    Модель жанра произведения.
    Используется в модели Произведения.
    описаны 2 поля: название категории и уникальный слаг для адресной строки
    """
    class Meta(NameSlug.Meta):
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
        max_length=NAME_LENGTH,
        verbose_name='Название',
    )
    year = models.PositiveIntegerField(
        validators=[MaxValueValidator(
            current_year,
            message=WRONG_YEAR_MESSAGE
        )],
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

    class Meta(NameSlug.Meta):
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
        return f'{self.title}_{self.genre}'


class BaseSettingModel(models.Model):
    """Модель для задания общих настроек к моделям Отзыв и Комментарий."""
    text = models.TextField('Текст')
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)
        default_related_name = '%(class)ss'

    def __str__(self):
        return self.text[:OUTPUT_LENGTH]


class Review(BaseSettingModel):
    """Модель Отзыв.
    Содержит данные о произведении, оценке, основной текс и автор отзыва,
    дата публикации отзыва.
    Настроена проверка значения оценки от 1 до 10.
    """
    title = models.ForeignKey(
        Title, verbose_name='Произведение', on_delete=models.CASCADE
    )
    score = models.SmallIntegerField(
        'Оценка произведения',
        validators=[
            MinValueValidator(
                1, message='Оценка должна быть больше или равна 1'
            ),
            MaxValueValidator(
                10, message='Оценка должна быть меньше или равна 10'
            ),
        ],
        default=1,
    )

    class Meta(BaseSettingModel.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'), name='unique_review'
            ),
        ]


class Comment(BaseSettingModel):
    """Модель Комментарий.
    Содержит данные об отзыве на произведение, основной текс и автор
    комментария, дата публикации комментария.
    """
    review = models.ForeignKey(
        Review, verbose_name='Отзыв', on_delete=models.CASCADE
    )

    class Meta(BaseSettingModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
