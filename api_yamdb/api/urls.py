from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserViewSet)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('titles', TitleViewSet, basename='title')
router_v1.register('categories', CategoryViewSet, basename='category')
router_v1.register('genres', GenreViewSet, basename='genre')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename="review"
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename="comment",
)
router_v1.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('v1/auth/signup/', views.signup_view, name='signup'),
    path('v1/auth/token/', views.get_token, name='get_token'),
    path('v1/', include(router_v1.urls)),
]
