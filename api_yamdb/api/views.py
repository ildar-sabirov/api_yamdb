from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import User
from .serializers import SignupSerializer, GetTokenSerializer


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
    pass


class CategoryViewSet(viewsets.ModelViewSet):
    pass


class GenreViewSet(viewsets.ModelViewSet):
    pass
