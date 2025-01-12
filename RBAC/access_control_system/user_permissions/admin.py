from django.contrib import admin
from .models import User, Role, Permission, Module

# Admin configuration for User model
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'role')
    ordering = ('username',)
    readonly_fields = ('created_at',)

# Admin configuration for Role model
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('created_at',)
    readonly_fields = ('created_at',)

# Admin configuration for Permission model
@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('created_at',)
    readonly_fields = ('created_at',)

# Admin configuration for Module model
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('created_at',)
    readonly_fields = ('created_at',)
