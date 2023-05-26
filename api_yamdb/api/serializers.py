from django.db.models import Avg
from django.utils.timezone import now
from rest_framework import serializers

from reviews.models import Category, Genre, Review, Title, TitleGenres


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
    score = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'name', 'year', 'description',
            'category', 'genre', 'score'
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
            current_genre_serialized = CategorySerializer(current_genre).data
            current_title_genres.append(current_genre_serialized)
        response['genre'] = current_title_genres
        return response

    def get_score(self, obj):
        review = Review.objects.filter(title=obj.pk)
        if review.exists():
            return int(review.aggregate(Avg('score')))
        return None

    def validate_year(self, data):
        year = int(data)
        if year > now().year:
            raise serializers.ValidationError(
                'Год издания не может быть больше текущего'
            )
        return data
