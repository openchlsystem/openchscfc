from django.urls import path
from .views import whatsapp_webhook, notify_user


urlpatterns = [
    path('webhook/', whatsapp_webhook, name='whatsapp_webhook_handler'),
    path('notify-user/', notify_user, name='notify_user'),
]
