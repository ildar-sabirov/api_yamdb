from rest_framework import serializers

from reviews.models import Category, Genre, Title, User


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
        fields = '__all__'
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Жанры."""

    class Meta:
        fields = '__all__'
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Произведения."""

    class Meta:
        fields = '__all__'
        model = Title
