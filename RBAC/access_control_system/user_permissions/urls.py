from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import UserViewSet, RoleViewSet, PermissionViewSet, ModuleViewSet

# Set up the router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'modules', ModuleViewSet, basename='module')

# Define app-specific URLs
urlpatterns = [
    path('api/', include(router.urls)),
]
