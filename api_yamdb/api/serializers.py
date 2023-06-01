from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault
from rest_framework.generics import get_object_or_404
from rest_framework.serializers import IntegerField

from reviews.models import (
    ROLE_CHOICES, Category, Comment, Genre, Review, Title, User,
)

INVALID_USERNAME = 'Недопустимый username'
USERNAME_IS_NOT_AVAILABLE = 'Пользователь с таким username уже существует'
EMAIL_IS_NOT_AVAILABLE = 'Пользователь с таким email уже существует'
GENRE_DOES_NOT_EXIST = 'Такого жанра не существует: {genre}.'
CANNOT_ADD_MORE_THAN_ONE_COMMENT = 'Нельзя добавить больше одного комментария'


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""
    email = serializers.EmailField(max_length=254)
    username = serializers.RegexField(regex=r'^[\w.@+-]+$', max_length=150)

    class Meta:
        fields = ('email', 'username')
        model = User

    def validate_username(self, username):
        if username.lower() == 'me':
            raise serializers.ValidationError(INVALID_USERNAME)
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                USERNAME_IS_NOT_AVAILABLE
            )
        return username

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                EMAIL_IS_NOT_AVAILABLE
            )
        return email


class GetTokenSerializer(serializers.ModelSerializer):
    """Сериализатор для получения JWT-токена."""
    username = serializers.RegexField(regex=r'^[\w.@+-]+$', max_length=150)
    confirmation_code = serializers.CharField()

    class Meta:
        fields = ('username', 'confirmation_code')
        model = User


class UserSerializer(SignupSerializer):
    """Сериализатор для работы с данными пользователей"""
    role = serializers.ChoiceField(choices=ROLE_CHOICES, required=False)

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
