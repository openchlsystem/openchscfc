from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from .models import User, Role, Permission, Module
from .serializers import UserSerializer, RoleSerializer, PermissionSerializer, ModuleSerializer


def check_permissions(user, permission_name):
    """
    Helper function to check if the user has the required permission.
    """
    if user.is_superuser:
        return  # Superusers bypass permission checks
    if not user.role or not user.role.permissions.filter(name=permission_name).exists():
        raise PermissionDenied(f"You do not have permission to {permission_name}.")


class RoleViewSet(viewsets.ModelViewSet):
    """
    Viewset for managing roles.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to view roles.")
        return super().get_queryset()

    def perform_create(self, serializer):
        check_permissions(self.request.user, "create_role")
        serializer.save()

    def perform_update(self, serializer):
        check_permissions(self.request.user, "update_role")
        serializer.save()

    def perform_destroy(self, instance):
        check_permissions(self.request.user, "delete_role")
        instance.delete()


class UserViewSet(viewsets.ModelViewSet):
    """
    Viewset for managing users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to view users.")
        return super().get_queryset()

    def perform_create(self, serializer):
        check_permissions(self.request.user, "create_user")
        serializer.save()

    def perform_update(self, serializer):
        check_permissions(self.request.user, "update_user")
        serializer.save()

    def perform_destroy(self, instance):
        check_permissions(self.request.user, "delete_user")
        instance.delete()


class PermissionViewSet(viewsets.ModelViewSet):
    """
    Viewset for managing permissions.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to view permissions.")
        return super().get_queryset()


class ModuleViewSet(viewsets.ModelViewSet):
    """
    Viewset for managing modules.
    """
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return super().get_queryset()
        if not self.request.user.role or not self.request.user.role.permissions.filter(name="view_module").exists():
            raise PermissionDenied("You do not have permission to view modules.")
        return super().get_queryset()

    def perform_create(self, serializer):
        check_permissions(self.request.user, "create_module")
        serializer.save()

    def perform_update(self, serializer):
        check_permissions(self.request.user, "update_module")
        serializer.save()

    def perform_destroy(self, instance):
        check_permissions(self.request.user, "delete_module")
        instance.delete()
