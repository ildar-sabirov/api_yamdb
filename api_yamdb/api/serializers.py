from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault
from rest_framework.generics import get_object_or_404
from rest_framework.serializers import IntegerField

from reviews.models import (Category, Comment, Genre, Review, Title, User)
from reviews.validators import validate_username

EMAIL_LENGTH = 254
USERNAME_LENGTH = 150
GENRE_DOES_NOT_EXIST = 'Такого жанра не существует: {genre}.'
CANNOT_ADD_MORE_THAN_ONE_COMMENT = 'Нельзя добавить больше одного комментария'


class SignupSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""
    email = serializers.EmailField(max_length=EMAIL_LENGTH)
    username = serializers.CharField(
        max_length=USERNAME_LENGTH, validators=[validate_username]
    )


class GetTokenSerializer(serializers.Serializer):
    """Сериализатор для получения JWT-токена."""
    username = serializers.CharField(
        max_length=USERNAME_LENGTH, validators=[validate_username]
    )
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с данными пользователей"""

    class Meta:
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        model = User


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Категории."""

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Жанры."""

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitlePostSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Произведения.
    Добавляет возможность записи новых объектов мадели Произведения
    с заданием полей категорий и жанров по слаг этих моделей.
    Добавляет к модели расчетное поле рейтинг: среднее значение поля
    'оценка произведения' модели Отзывов, связанных с выбранным произведением.
    Настраивает отображение для методов GET объекта модели Произведения
    с выводом имени и слага для категорий и жанров.
    """
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        write_only=True,
        many=True
    )

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug', write_only=True
    )

    class Meta:
        fields = (
            'id', 'name', 'year', 'description',
            'category', 'genre'
        )
        model = Title


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Произведения.
    Добавляет возможность записи новых объектов мадели Произведения
    с заданием полей категорий и жанров по слаг этих моделей.
    Добавляет к модели расчетное поле рейтинг: среднее значение поля
    'оценка произведения' модели Отзывов, связанных с выбранным произведением.
    Настраивает отображение для методов GET объекта модели Произведения
    с выводом имени и слага для категорий и жанров.
    """
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = (
            'id', 'name', 'year', 'description',
            'category', 'genre', 'rating',
        )
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        default=CurrentUserDefault(),
        slug_field="username", read_only=True
    )
    score = IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    def validate(self, data):
        request = self.context["request"]
        if request.method == "POST":
            author = request.user
            title_id = self.context["view"].kwargs.get("title_id")
            title = get_object_or_404(Title, pk=title_id)
            if Review.objects.filter(title=title, author=author).exists():
                raise ValidationError(CANNOT_ADD_MORE_THAN_ONE_COMMENT)
        return data

    class Meta:
        fields = ("id", "text", "author", "score", "pub_date", "title")
        model = Review
        read_only_fields = ("title",)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field="username")

    class Meta:
        fields = ("id", "text", "author", "pub_date")
        model = Comment
        read_only_fields = ("review",)
