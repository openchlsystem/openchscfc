
import json
import logging
import requests
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import IncomingMessage, OutgoingMessage
from .serializers import IncomingMessageSerializer, OutgoingMessageSerializer
from .utils import get_access_token  # Assume this function is well implemented
from rest_framework import generics
from django_filters import rest_framework as filters


# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'GET':
        return handle_verification_request(request)
    elif request.method == 'POST':
        return handle_incoming_messages(request)
    else:
        logging.warning(f"Received invalid HTTP method: {request.method}")
        return HttpResponseBadRequest("Invalid HTTP method. This endpoint expects a GET or POST request.")


def handle_incoming_messages(request):
    try:
        # Parse the JSON body of the request
        data = json.loads(request.body.decode('utf-8'))
        logging.debug(f'Incoming message data: {data}')

        # Print the complete JSON data structure with indentation for better readability
        logging.info(json.dumps(data, indent=4))  # This line logs the object

        # You will need to adjust the parsing logic based on the actual data structure sent by WhatsApp
        for message in data.get('messages', []):
            # Assuming 'from' and 'text' are keys in the JSON data structure
            IncomingMessage.objects.create(
                contact_wa_id=message['from'],
                message_text=message['text']['body']
            )

        # Respond back to WhatsApp to acknowledge receipt of the messages
        return JsonResponse({'status': 'Success', 'message': 'Messages received and saved successfully'})
    except Exception as e:
        logging.error(f'Error handling incoming message: {str(e)}')
        return HttpResponseBadRequest(f"Error handling incoming message: {str(e)}")


def handle_verification_request(request):
    hub_mode = request.GET.get('hub.mode')
    hub_challenge = request.GET.get('hub.challenge')
    hub_verify_token = request.GET.get('hub.verify_token')
    
    logging.debug(f"Received verification request with mode={hub_mode}, challenge={hub_challenge}, token={hub_verify_token}")
    if hub_mode == 'subscribe' and hub_verify_token == settings.VERIFICATION_TOKEN:
        logging.info("Webhook verified successfully with challenge: " + hub_challenge)
        return JsonResponse(int(hub_challenge), safe=False, status=200)
    else:
        # logging.error("Verification failed with the provided token: " + hub_verify_token)
        return HttpResponseBadRequest("Verification failed. Check your verification token.")

@csrf_exempt
def receive_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            IncomingMessage.objects.create(
                contact_wa_id=data['from'],
                message_text=data['text']['body']
            )
            return JsonResponse({'status': 'Success', 'message': 'Message received and saved'})
        except Exception as e:
            logging.error(f'Error receiving message: {str(e)}')
            return HttpResponseBadRequest(f"Error processing message: {str(e)}")
    else:
        return HttpResponseBadRequest("Invalid request method. Only POST requests are accepted.")


@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            recipient = data['recipient']
            message = data['message']
            access_token = get_access_token()
            response = send_whatsapp_message(access_token, recipient, message)
            OutgoingMessage.objects.create(
                contact_wa_id=recipient,
                message_text=message,
                was_successful=response['success'] if response else False
            )
            return JsonResponse({'status': 'Success', 'response': 'Message sent and logged'})
        except Exception as e:
            logging.error(f"Failed to send message: {str(e)}")
            return JsonResponse({'status': 'Error', 'message': str(e)}, status=400)
    else:
        return HttpResponseBadRequest("This endpoint only supports POST requests.")

@receiver(post_save, sender=OutgoingMessage)
def send_whatsapp_message_on_create(sender, instance, created, **kwargs):
    if created:
        access_token = get_access_token()
        recipient = instance.contact_wa_id
        message = instance.message_text
        send_whatsapp_message(access_token, recipient, message)

def send_whatsapp_message(access_token, recipient, message):
    endpoint_url = "https://graph.facebook.com/v18.0/101592599705197/messages"
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    request_body = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "text",
        "text": {"preview_url": False, "body": message}
    }

    try:
        response = requests.post(endpoint_url, json=request_body, headers=headers)
        response.raise_for_status()
        logging.info("Message sent successfully.")
        return {'success': True}
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending message: {e}")
        return {'success': False}

class incomingMessageList(generics.ListCreateAPIView):
    queryset = IncomingMessage.objects.all()
    serializer_class = IncomingMessageSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['contact_wa_id']
    
class outgoingMessageList(generics.ListCreateAPIView):
    queryset = OutgoingMessage.objects.all()
    serializer_class = OutgoingMessageSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['contact_wa_id']













# New code for sending messages to WhatsApp


# import json
# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# from .services import send_whatsapp_message
# from .utils import decode_and_save_message
# import logging

# logger = logging.getLogger(__name__)

# @csrf_exempt
# def whatsapp_webhook(request):
#     if request.method == "POST":
#         try:
#             # Parse the incoming JSON payload
#             payload = json.loads(request.body)

#             # Extract the first message from the payload
#             message_data = payload['entry'][0]['changes'][0]['value']['messages'][0]
#             metadata = payload['entry'][0]['changes'][0]['value']['metadata']

#             # Derive the phone_number_id
#             phone_number_id = metadata.get("phone_number_id")

#             # Decode and save the message
#             access_token = "19021977"
#             message = decode_and_save_message(message_data, phone_number_id, access_token)

#             if message:
#                 return JsonResponse({"status": "success"}, status=200)
#             else:
#                 return JsonResponse({"status": "error", "message": "Failed to process message"}, status=400)

#         except KeyError as e:
#             logger.error(f"Missing key in payload: {e}")
#             return JsonResponse({"error": f"Missing key: {e}"}, status=400)
#         except Exception as e:
#             logger.error(f"Error processing webhook: {e}")
#             return JsonResponse({"error": str(e)}, status=500)
#     else:
#         return JsonResponse({"message": "Invalid method"}, status=405)

# """
# Sample Payload:

# {
#   "object": "whatsapp_business_account",
#   "entry": [
#     {
#       "id": "1234567890",
#       "changes": [
#         {
#           "value": {
#             "messaging_product": "whatsapp",
#             "metadata": {
#               "display_phone_number": "15551234567",
#               "phone_number_id": "123456789012345"
#             },
#             "contacts": [
#               {
#                 "profile": {
#                   "name": "John Doe"
#                 },
#                 "wa_id": "1234567890"
#               }
#             ],
#             "messages": [
#               {
#                 "from": "1234567890",
#                 "id": "ABCD1234",
#                 "timestamp": "1672531200",
#                 "type": "text",
#                 "text": {
#                   "body": "Hello, this is a test message!"
#                 }
#               }
#             ]
#           },
#           "field": "messages"
#         }
#       ]
#     }
#   ]
# }

# """

def notify_user(request):
    """
    View to send a WhatsApp message to a user.
    """
    phone_number = "+1234567890"
    message = "Hello, this is a test message from our Django app."
    response = send_whatsapp_message(phone_number, message)
    return JsonResponse(response)
