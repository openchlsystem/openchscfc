# from rest_framework.permissions import BasePermission
# from .models import RolePermission, Permission

# class HasPermission(BasePermission):
#     def has_permission(self, request, view):
#         user = request.user
#         if user.is_superuser:
#             return True  # Superusers have all permissions
        
#         action = view.action  # Current action (e.g., list, create, update, delete)
#         required_permission = f"{view.basename}_{action}"  # Permission naming: user_list, user_create, etc.

#         try:
#             role_permissions = RolePermission.objects.filter(role=user.role)
#             permissions = [role_permission.permission.name for role_permission in role_permissions]
#             return required_permission in permissions
#         except RolePermission.DoesNotExist:
#             return False
