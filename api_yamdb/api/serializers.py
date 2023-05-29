from django.db.models import Avg
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault
from rest_framework.serializers import IntegerField

from reviews.models import (Category, Genre, Review, TitleGenres,
                            Title, User, Comment)


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя."""
    email = serializers.EmailField(max_length=254)
    username = serializers.RegexField(regex=r'^[\w.@+-]+$', max_length=150)

    class Meta:
        fields = ('email', 'username')
        model = User


class GetTokenSerializer(serializers.ModelSerializer):
    """Сериализатор для получения JWT-токена."""
    username = serializers.RegexField(regex=r'^[\w.@+-]+$', max_length=150)
    confirmation_token = serializers.CharField()

    class Meta:
        fields = ('username', 'confirmation_token')
        model = User


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Категории."""

    class Meta:
        fields = ('name', 'slug')
        model = Category
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Жанры."""

    class Meta:
        fields = ('name', 'slug')
        model = Genre
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Произведения."""
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
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'name', 'year', 'description',
            'category', 'genre', 'rating'
        )
        model = Title

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
            try:
                current_genre = Genre.objects.get(slug=genre)
            except Exception:
                raise serializers.ValidationError(
                    f'Такого жанра не существует: {genre}.'
                )
            TitleGenres.objects.create(
                genre=current_genre, title=title)
        return title

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['category'] = CategorySerializer(instance.category).data

        id_title = instance.id
        genres = TitleGenres.objects.filter(
            title=id_title
        ).values_list('genre', flat=True)
        current_title_genres = []
        for genre_id in genres:
            current_genre = Genre.objects.get(pk=genre_id)
            current_genre_serialized = GenreSerializer(current_genre).data
            current_title_genres.append(current_genre_serialized)
        response['genre'] = current_title_genres
        return response

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg('score'))
        return rating.get('score__avg')

    def validate_year(self, data):
        year = int(data)
        if year > now().year:
            raise serializers.ValidationError(
                'Год издания не может быть больше текущего'
            )
        return data


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
                raise ValidationError("Нельзя добавить больше 1 комментария")
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
