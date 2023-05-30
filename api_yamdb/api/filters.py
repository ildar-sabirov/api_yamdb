from django_filters import rest_framework as filters

from reviews.models import Title


class TitleFilter(filters.FilterSet):
    """Настройки фильтрации для модели Произведения.
    Добавляет фильтрацию по полям слаг для категорий и жанров,
    а так же по названию произведения и году издания.
    """
    category = filters.CharFilter(
        field_name="category__slug", lookup_expr='exact'
    )
    genre = filters.CharFilter(field_name="genre__slug", lookup_expr='exact')

    class Meta:
        model = Title
        fields = ['name', 'year']
