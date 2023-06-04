from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrAuthorOrReadOnly(BasePermission):
    """Для аутентифицированных пользователей имеющих статус администратора или
    автора иначе только просмотр."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )


class IsAdmin(BasePermission):
    """Для аутентифицированных пользователей имеющих статус администратора."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdminOrReadOnly(IsAdmin):
    """Для администратора и суперюзера иначе только просмотр."""

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or super().has_permission(request, view)
        )
