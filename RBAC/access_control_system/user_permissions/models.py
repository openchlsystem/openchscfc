from django.db import models
from django.contrib.auth.models import AbstractUser, Group

# Permission Model
class Permission(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# Module Model
class Module(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# Role Model
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    modules = models.ManyToManyField(Module, related_name="roles", blank=True)  # Many-to-Many with Modules
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# RolePermissions Model (Intermediate Model)
class RolePermissions(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_permissions")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="role_permissions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('role', 'permission')  # Ensure no duplicate entries

    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"


# Custom User Model
class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    groups = models.ManyToManyField(Group, related_name="custom_user_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions_set", blank=True)

    def __str__(self):
        return self.username

    def get_permissions(self):
        """Retrieve all permissions associated with the user's role."""
        if self.role:
            # Use RolePermissions to fetch permissions explicitly
            return Permission.objects.filter(role_permissions__role=self.role)
        return Permission.objects.none()  # Return no permissions if the user has no role

    def get_modules(self):
        """Retrieve all modules associated with the user's role."""
        if self.role:
            return self.role.modules.all()  # Get modules from the user's role
        return Module.objects.none()  # Return no modules if the user has no role