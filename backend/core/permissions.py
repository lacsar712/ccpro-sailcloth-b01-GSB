"""角色权限：分界设置读开放给登录用户，写仅管理员。"""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminForWrite(BasePermission):
    """GET/HEAD/OPTIONS 放行；写操作要求 user.role == admin。"""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) == user.ROLE_ADMIN
        )
