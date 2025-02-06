from django.urls import path
from .views import (
    WhatsAppMessageList,
    WhatsAppMediaList,
    ContactList,
    IncomingMessageList,
    OutgoingMessageList,
    send_message,
    whatsapp_webhook,
    # notify_user
)

urlpatterns = [
    # Webhook for WhatsApp verification & message handling
    path('webhook/', whatsapp_webhook, name='whatsapp_webhook'),

    # URL for sending WhatsApp messages
    path('whatsapp/send/', send_message, name='send_message'),

    # Notify user via WhatsApp (optional test endpoint)
    # path('notify-user/', notify_user, name='notify_user'),

    # API Endpoints for WhatsApp Message, Media, and Contacts
    path('whatsapp/messages/', WhatsAppMessageList.as_view(), name='whatsapp_messages'),
    path('whatsapp/messages/incoming/', IncomingMessageList.as_view(), name='incoming_messages'),
    path('whatsapp/messages/outgoing/', OutgoingMessageList.as_view(), name='outgoing_messages'),
    path('whatsapp/media/', WhatsAppMediaList.as_view(), name='whatsapp_media'),
    path('whatsapp/contacts/', ContactList.as_view(), name='whatsapp_contacts'),
]
