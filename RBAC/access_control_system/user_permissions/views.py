from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from .models import User, Role, Permission, Module
from .serializers import UserSerializer, RoleSerializer, PermissionSerializer, ModuleSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def get_queryset(self):
        # Allow superusers unrestricted access
        if self.request.user.is_superuser:
            return super().get_queryset()

        # For non-superusers, check for user_id and permissions
        user_id = self.request.query_params.get('user_id')
        if not user_id:
            raise PermissionDenied("User ID is required to access roles.")

        user = User.objects.filter(id=user_id).first()
        if not user or not user.role:
            raise PermissionDenied("You do not have permission to view roles.")

        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        # Restrict creation to superusers
        if not request.user.is_superuser:
            raise PermissionDenied("Only superusers can create roles.")

        return super().create(request, *args, **kwargs)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        
        # If no user_id is provided and the requester is a superuser, allow full access
        if not user_id:
            if self.request.user.is_superuser:
                return super().get_queryset()
            raise PermissionDenied("User ID is required to access users.")

        # Check if the user exists and has a role
        user = User.objects.filter(id=user_id).first()
        if not user or not user.role:
            raise PermissionDenied("You do not have permission to view users.")

        return super().get_queryset()

    def perform_create(self, serializer):
        user_id = self.request.query_params.get('user_id')

        # Allow superusers to create users without restrictions
        if self.request.user.is_superuser:
            serializer.save()
            return

        # Validate permission for non-superusers
        if not user_id:
            raise PermissionDenied("User ID is required to create users.")

        user = User.objects.filter(id=user_id).first()
        if not user or not user.is_superuser:
            raise PermissionDenied("Only superusers can create users.")

        serializer.save()

    def perform_update(self, serializer):
        user_id = self.request.query_params.get('user_id')

        # Allow superusers to update users without restrictions
        if self.request.user.is_superuser:
            serializer.save()
            return

        # Validate permission for non-superusers
        if not user_id:
            raise PermissionDenied("User ID is required to update users.")

        user = User.objects.filter(id=user_id).first()
        if not user or not user.is_superuser:
            raise PermissionDenied("Only superusers can update users.")

        serializer.save()

    def perform_destroy(self, instance):
        user_id = self.request.query_params.get('user_id')

        # Allow superusers to delete users without restrictions
        if self.request.user.is_superuser:
            instance.delete()
            return

        # Validate permission for non-superusers
        if not user_id:
            raise PermissionDenied("User restricted to delete users.")

        user = User.objects.filter(id=user_id).first()
        if not user or not user.is_superuser:
            raise PermissionDenied("Only superusers can delete users.")

        instance.delete()

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    def get_queryset(self):
        # Check if the user is a superuser
        if not self.request.user.is_superuser:
            raise PermissionDenied("You do not have permission to view permissions.")

        return super().get_queryset()

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

    def get_queryset(self):
        # Simulate permission logic based on user_id query parameter
        user_id = self.request.query_params.get('user_id')
        if not user_id:
            raise PermissionDenied("User ID is required to access modules.")

        user = User.objects.filter(id=user_id).first()
        if not user or not user.role:
            raise PermissionDenied("You do not have permission to view modules.")

        return super().get_queryset()
