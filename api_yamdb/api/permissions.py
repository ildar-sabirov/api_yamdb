from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrOwnerOrReadOnly(BasePermission):
    """Для аутентифицированных пользователей имеющих статус администратора или
    автора иначе только просмотр."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_admin
            or request.user.is_moderator
            or obj.author == request.user
        )
