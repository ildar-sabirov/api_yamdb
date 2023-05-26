from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import CategoryViewSet, GenreViewSet, TitleViewSet

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('titles', TitleViewSet, basename='title')
router_v1.register('categories', CategoryViewSet, basename='category')
router_v1.register('genres', GenreViewSet, basename='genre')

urlpatterns = [
    path('v1/auth/signup/', views.signup_view, name='signup'),
    path('v1/auth/token/', views.get_token, name='get_token'),
    path('v1/', include(router_v1.urls)),
]
