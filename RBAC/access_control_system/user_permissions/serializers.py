from rest_framework import serializers
from .models import Module, Permission, Role, RolePermissions, User


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = '__all__'


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    role_permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(), many=True  # No need for 'source' argument
    )
    modules = serializers.PrimaryKeyRelatedField(queryset=Module.objects.all(), many=True)

    class Meta:
        model = Role
        fields = '__all__'

    def create(self, validated_data):
        permissions_data = validated_data.pop('role_permissions', [])
        modules_data = validated_data.pop('modules', [])
        role = Role.objects.create(**validated_data)

        # Assign modules
        role.modules.set(modules_data)

        # Create role-permission mappings
        for permission in permissions_data:
            RolePermissions.objects.create(role=role, permission=permission)

        return role

    def update(self, instance, validated_data):
        permissions_data = validated_data.pop('role_permissions', [])
        modules_data = validated_data.pop('modules', [])

        # Update role fields
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        # Update modules
        instance.modules.set(modules_data)

        # Update role-permission mappings
        RolePermissions.objects.filter(role=instance).delete()
        for permission in permissions_data:
            RolePermissions.objects.create(role=instance, permission=permission)

        return instance




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'role',
            'date_joined', 'is_staff', 'is_active', 'is_superuser',
            'created_at', 'updated_at', 'groups', 'user_permissions'
        ]
        read_only_fields = ['id', 'date_joined', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Handle password hashing
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        # Handle password updates securely
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user