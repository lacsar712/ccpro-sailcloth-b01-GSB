from rest_framework.permissions import BasePermission

from accounts.models import User


class IsAdminRole(BasePermission):
    """仅角色为管理员（admin）可写；操作工等其余角色一律拒绝。"""

    message = "仅管理员可修改克重色带分界"

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and user.role == User.ROLE_ADMIN
        )
