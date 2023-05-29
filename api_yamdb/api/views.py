from api.permissions import IsAdminOrAuthorOrReadOnly, IsAdminOrReadOnly
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title, User
from .filters import TitleFilter
from .mixins import CreateListDestroyViewSet
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTokenSerializer,
                          ReviewSerializer, SignupSerializer, TitleSerializer)


@api_view(['POST'])
def signup_view(request):
    """Регистрация пользователя и отправка кода подтверждения по почте."""
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        confirmation_token = default_token_generator.make_token(user)
        send_mail(
            'Confirmation token',
            f'Код подтверждения для получения токена: {confirmation_token}',
            'from@example.com',
            [serializer.data.get('email')],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_token(request):
    """Получение токена по имени пользователя и коду подтверждения."""
    serializer = GetTokenSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data.get('username')
        confirmation_token = serializer.validated_data.get(
            'confirmation_token'
        )
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, confirmation_token):
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {'token': str(RefreshToken.for_user(user).access_token)},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TitleViewSet(viewsets.ModelViewSet):
    """Просмотр произведений.
    Доступны просмотр списка всех объектов без токена,
    добавление, частичное изменение и удаление только для администратора
    и суперюзера.
    Настроена пагинация и фильтрация по полям: слаг категории, слаг жанра,
    название произведения и год издания.
    """
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']


class CategoryViewSet(CreateListDestroyViewSet):
    """Просмотр категорий.
    Доступны просмотр списка всех объектов без токена,
    добавление и удаление только для администратора и суперюзера.
    Настроена пагинация и поиск по полю название.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
    """Просмотр жанров.
    Доступны просмотр списка всех объектов без токена,
    добавление и удаление только для администратора и суперюзера.
    Настроена пагинация и поиск по полю название.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminOrAuthorOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get("title_id"))

    def get_queryset(self):
        return self.get_title().reviews.select_related("author")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminOrAuthorOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get("review_id"))

    def get_queryset(self):
        return self.get_review().comments.select_related("author")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
