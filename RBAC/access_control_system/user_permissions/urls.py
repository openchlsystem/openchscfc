from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ModuleViewSet, PermissionViewSet, RoleViewSet, UserViewSet

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'modules', ModuleViewSet, basename='modules')
router.register(r'permissions', PermissionViewSet, basename='permissions')
router.register(r'roles', RoleViewSet, basename='roles')
router.register(r'users', UserViewSet, basename='users')

# Define urlpatterns
urlpatterns = [
    # Include all routes registered in the router
    path('', include(router.urls)),
]