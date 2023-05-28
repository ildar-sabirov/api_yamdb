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
            or request.user.role == 'moderator'
            or request.user.role == 'admin'
            or request.user.is_superuser
        )


class IsAdminOrReadOnly(BasePermission):
    """Для администратора и суперюзера иначе только просмотр."""

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        else:
            if request.user.is_authenticated:
                return (
                    request.user.role == 'admin'
                    or request.user.is_superuser
                )
        return False

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.role == 'admin'
            or request.user.is_superuser
        )
