import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .services import send_whatsapp_message
from .utils import decode_and_save_message
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "POST":
        try:
            # Parse the incoming JSON payload
            payload = json.loads(request.body)

            # Extract the first message from the payload
            message_data = payload['entry'][0]['changes'][0]['value']['messages'][0]
            metadata = payload['entry'][0]['changes'][0]['value']['metadata']

            # Derive the phone_number_id
            phone_number_id = metadata.get("phone_number_id")

            # Decode and save the message
            access_token = "your-whatsapp-api-access-token"
            message = decode_and_save_message(message_data, phone_number_id, access_token)

            if message:
                return JsonResponse({"status": "success"}, status=200)
            else:
                return JsonResponse({"status": "error", "message": "Failed to process message"}, status=400)

        except KeyError as e:
            logger.error(f"Missing key in payload: {e}")
            return JsonResponse({"error": f"Missing key: {e}"}, status=400)
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Invalid method"}, status=405)

"""
Sample Payload:

{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "1234567890",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "15551234567",
              "phone_number_id": "123456789012345"
            },
            "contacts": [
              {
                "profile": {
                  "name": "John Doe"
                },
                "wa_id": "1234567890"
              }
            ],
            "messages": [
              {
                "from": "1234567890",
                "id": "ABCD1234",
                "timestamp": "1672531200",
                "type": "text",
                "text": {
                  "body": "Hello, this is a test message!"
                }
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}

"""

def notify_user(request):
    """
    View to send a WhatsApp message to a user.
    """
    phone_number = "+1234567890"
    message = "Hello, this is a test message from our Django app."
    response = send_whatsapp_message(phone_number, message)
    return JsonResponse(response)
