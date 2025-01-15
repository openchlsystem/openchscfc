from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Module, Permission, Role, RolePermissions, User
from .serializers import ModuleSerializer, PermissionSerializer, RoleSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['get'], url_path='permissions_by_module')
    def permissions_by_module(self, request, pk=None):
        user = self.get_object()
        module_id = request.query_params.get('module_id')

        if not module_id:
            return Response({"error": "module_id is required."}, status=400)

        try:
            module = Module.objects.get(id=module_id)
        except Module.DoesNotExist:
            return Response({"error": "Module not found."}, status=404)

        # Get permissions linked to the user's role and the module
        if user.role:
            permissions = Permission.objects.filter(
                role_permissions__role=user.role,
                role_permissions__module=module  # Ensure the module is linked to the role permission
            ).distinct()
        else:
            permissions = Permission.objects.none()

        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

    @action(detail=True, methods=['get'], url_path='permissions')
    def permissions(self, request, pk=None):
        module = self.get_object()

        # Get permissions associated with this module
        permissions = Permission.objects.filter(
            role_permissions__module=module
        ).distinct()

        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    @action(detail=True, methods=['get'], url_path='permissions')
    def permissions(self, request, pk=None):
        role = self.get_object()

        # Get permissions associated with this role
        permissions = Permission.objects.filter(
            role_permissions__role=role
        ).distinct()

        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    # You could also add actions for permission management here, e.g., to link permissions to roles or modules
    # Example: @action(detail=True, methods=['post'], url_path='assign_to_role')
    #           def assign_to_role(self, request, pk=None):
    #               ...