from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import TitleFilter
from .permissions import IsAdmin, IsAdminOrAuthorOrReadOnly, IsAdminOrReadOnly
from .serializers import (
    CategorySerializer, CommentSerializer, GenreSerializer, GetTokenSerializer,
    ReviewSerializer, SignupSerializer, TitlePostSerializer, TitleSerializer,
    UserSerializer,
)
from api_yamdb.settings import FROM_EMAIL
from reviews.models import Category, Genre, Review, Title, User

USERNAME_OR_EMAIL_UNAVAILABLE = (
    'Пользователь с таким {field_name} уже существует.'
)
SUBJECT_LINE = 'Confirmation code'
EMAIL_TEXT = 'Код подтверждения для получения токена: {confirmation_code}'


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def signup_view(request):
    """Регистрация пользователя и отправка кода подтверждения по почте."""
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.data.get('username')
    email = serializer.data.get('email')
    try:
        user, _ = User.objects.get_or_create(username=username, email=email)
    except IntegrityError:
        field_name = 'username' if User.objects.filter(
            username=username
        ).exists() else 'email'
        raise serializers.ValidationError(
            USERNAME_OR_EMAIL_UNAVAILABLE.format(field_name=field_name)
        )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        SUBJECT_LINE,
        EMAIL_TEXT.format(confirmation_code=confirmation_code),
        FROM_EMAIL,
        [serializer.data.get('email')],
        fail_silently=False,
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def get_token(request):
    """Получение токена по имени пользователя и коду подтверждения."""
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get(
        'confirmation_code'
    )
    user = get_object_or_404(User, username=username)
    if not default_token_generator.check_token(user, confirmation_code):
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
    return Response(
        {'token': str(RefreshToken.for_user(user).access_token)},
        status=status.HTTP_200_OK
    )


class UserViewSet(viewsets.ModelViewSet):
    """Просмотр профилей пользователей.
    Доступны просмотр списка всех объектов, и добавление, частичное изменение
    и удаление только для администратора и суперюзера.
    Для пользователя доступны просмотр своего профиля и частичное изменение.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (SearchFilter, )
    search_fields = ('username', )
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

    @action(
        detail=False, methods=['get', 'patch'], url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def owner_profile(self, request):
        user = request.user
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryGenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Ограничение доступных методов для запросов http (GET, POST, DELETE).
    Добавляет настройки доступа - для Администраторов или только на чтение,
    а так же возможность поиска по полю 'имя'
    """
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Просмотр произведений.
    Доступны просмотр списка всех объектов без токена,
    добавление, частичное изменение и удаление только для администратора
    и суперюзера.
    Настроена пагинация и фильтрация по полям: слаг категории, слаг жанра,
    название произведения и год издания.
    """
    queryset = Title.objects.annotate(rating=Avg('reviews__score')).all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    ordering = ('name',)
    filterset_class = TitleFilter
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method not in SAFE_METHODS:
            return TitlePostSerializer
        return TitleSerializer


class CategoryViewSet(CategoryGenreViewSet):
    """Просмотр категорий.
    Доступны просмотр списка всех объектов без токена,
    добавление и удаление только для администратора и суперюзера.
    Настроена пагинация и поиск по полю название.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CategoryGenreViewSet):
    """Просмотр жанров.
    Доступны просмотр списка всех объектов без токена,
    добавление и удаление только для администратора и суперюзера.
    Настроена пагинация и поиск по полю название.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminOrAuthorOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminOrAuthorOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
