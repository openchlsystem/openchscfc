from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from .models import User, Role, Permission, Module
from .serializers import UserSerializer, RoleSerializer, PermissionSerializer, ModuleSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def get_queryset(self):
        # Only superusers can view roles
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to view roles.")
        return super().get_queryset()

    def perform_create(self, serializer):
        # Only superusers can create roles
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to create roles.")
        serializer.save()

    def perform_update(self, serializer):
        # Only superusers can update roles
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to update roles.")
        serializer.save()

    def perform_destroy(self, instance):
        # Only superusers can delete roles
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to delete roles.")
        instance.delete()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        # Only superusers can view all users
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to view users.")
        return super().get_queryset()

    def perform_create(self, serializer):
        # Only superusers can create users
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to create users.")
        serializer.save()

    def perform_update(self, serializer):
        # Only superusers can update users
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to update users.")
        serializer.save()

    def perform_destroy(self, instance):
        # Only superusers can delete users
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to delete users.")
        instance.delete()


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    def get_queryset(self):
        # Only superusers can view permissions
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to view permissions.")
        return super().get_queryset()


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

    def get_queryset(self):
        # Check if the user has the required permission to view modules
        if not self.request.user.is_superuser and not self.request.user.role.permissions.filter(name="view_module").exists():
            raise PermissionDenied("You do not have permission to view modules.")
        return super().get_queryset()

    def perform_create(self, serializer):
        # Only users with the 'create_module' permission can create modules
        if not self.request.user.is_superuser and not self.request.user.role.permissions.filter(name="create_module").exists():
            raise PermissionDenied("You do not have permission to create modules.")
        serializer.save()

    def perform_update(self, serializer):
        # Only users with the 'update_module' permission can update modules
        if not self.request.user.is_superuser and not self.request.user.role.permissions.filter(name="update_module").exists():
            raise PermissionDenied("You do not have permission to update modules.")
        serializer.save()

    def perform_destroy(self, instance):
        # Only users with the 'delete_module' permission can delete modules
        if not self.request.user.is_superuser and not self.request.user.role.permissions.filter(name="delete_module").exists():
            raise PermissionDenied("You do not have permission to delete modules.")
        instance.delete()
