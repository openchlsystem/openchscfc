from django.urls import path
from .views import UnifiedWebhookView

urlpatterns = [
    # Single endpoint for all platform communication
    path('webhook/<str:platform>/', UnifiedWebhookView.as_view(), name='unified-webhook'),
]