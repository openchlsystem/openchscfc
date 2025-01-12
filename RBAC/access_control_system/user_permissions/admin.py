from django.contrib import admin

# Register your models here.
from .models import User, Role, Permission, Module, RolePermission, RoleModule

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff', 'is_superuser')

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'permission')

@admin.register(RoleModule)
class RoleModuleAdmin(admin.ModelAdmin):
    list_display = ('role', 'module')

