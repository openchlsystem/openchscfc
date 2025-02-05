from django.urls import path
from .views import incomingMessageList, outgoingMessageList, receive_message, send_message, whatsapp_webhook, notify_user


urlpatterns = [
    # path('webhook/', whatsapp_webhook, name='whatsapp_webhook_handler'),
    path('notify-user/', notify_user, name='notify_user'),
    
    # URL for WhatsApp webhook verification and message handling
    path('webhook/', whatsapp_webhook, name='whatsapp_webhook'),

    # URL for receiving incoming messages (if separate from webhook)
    path('whatsapp/receive/', receive_message, name='receive_message'),

    # URL for sending WhatsApp messages
    path('whatsapp/send/', send_message, name='send_message'),
    
    path('incomingmessages/', incomingMessageList.as_view(), name='incomingmessages'),
    path('outgoingmessages/', outgoingMessageList.as_view(), name='outgoingmessages'),
]
