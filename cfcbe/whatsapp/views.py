import json
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .services import send_whatsapp_message

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "POST":
        data = json.loads(request.body)
        # Process incoming messages
        return JsonResponse({"status": "received"})
    return JsonResponse({"error": "Invalid request"}, status=400)



def notify_user(request):
    """
    View to send a WhatsApp message to a user.
    """
    phone_number = "+1234567890"
    message = "Hello, this is a test message from our Django app."
    response = send_whatsapp_message(phone_number, message)
    return JsonResponse(response)
