import json
import logging
import base64
import requests
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Complaint, Notification

API_URL = "http://127.0.0.1:8000/api/feedback/complaints/"
HEADERS = {
    "Content-Type": "application/json",
<<<<<<< HEAD
    # "Authorization": "Bearer sccjqsonvfvro3v2pn80iat2me",
=======
    "Authorization": "Bearer sci9de994iddqlmj8fv7r1js74",
>>>>>>> 8f90d6105c60537cd2f201080ae7dc0238ffeb4a
}

@receiver(post_save, sender=Complaint)
def generate_notification(sender, instance, created, **kwargs):
    """Handles notification creation and API request for complaints."""
    
    # Refresh instance to ensure related data is loaded
    instance.refresh_from_db()

    # Extract victim and perpetrator details safely
    victim = instance.victim
    perpetrator = instance.perpetrator

    victim_info = (
        f"Victim: {victim.name} Age: {victim.age or 'N/A'}, Gender: {victim.gender or 'N/A'}"
        if victim else "No victim data provided."
    )
    perpetrator_info = (
        f"Perpetrator: {perpetrator.name} Age: {perpetrator.age or 'N/A'}, Gender: {perpetrator.gender or 'N/A'}"
        if perpetrator else "No perpetrator data provided."
    )

    print(f"Victim data: {victim}")
    print(f"Perpetrator data: {perpetrator}")

    # Construct complaint data
    complaint_data = {
        "complaint_id": str(instance.complaint_id),
        "channel": "chat",
        "timestamp": instance.timestamp.isoformat(),
        "session_id": str(instance.session_id),
        "message_id": str(instance.complaint_id),
        "from": str(instance.session_id),
        "reporter_nickname": instance.reporter_nickname,
        "case_category": instance.case_category,
        "victim": {
            "name": victim.name if victim else "",
            "age": victim.age if victim else "",
            "gender": victim.gender if victim else "",
        },
        "perpetrator": {
            "name": perpetrator.name if perpetrator else "",
            "age": perpetrator.age if perpetrator else "",
            "gender": perpetrator.gender if perpetrator else "",
        },
    }

    print(f"Complaint object: {complaint_data}")

    # Convert to JSON and encode in Base64
    complaint_json = json.dumps(complaint_data)
    encoded_data = base64.b64encode(complaint_json.encode()).decode("utf-8")

    print(f"Base64 encoded data: {encoded_data}")

    # Construct final payload for API
    complaint_payload = {
        "channel": "chat",
        "timestamp": instance.timestamp.isoformat(),
        "session_id": str(instance.session_id),
        "message_id": str(instance.complaint_id),
        "from": str(instance.session_id),
        "message": encoded_data,
        "mime": "application/json",
    }

    json_payload = json.dumps(complaint_payload)
    print(f"JSON payload: {json_payload}")

    # Construct notification message
    notification_message = (
        f"A new complaint has been filed by {instance.reporter_nickname or 'an anonymous reporter'} "
        f"in the category {instance.case_category}. {victim_info} {perpetrator_info}"
    )

    print(f"Notification: {notification_message}")

    # Save Notification
    Notification.objects.create(
        complaint=instance,
        message=notification_message
    )

    # Send the complaint to API
    try:
        response = requests.post(API_URL, headers=HEADERS, json=complaint_payload)
        print(f"API Response: {response.status_code}, {response.text}")

        if response.status_code == 201:
            response_data = response.json()

            # Extract message_id from API response
            message_id = response_data.get("messages", [[]])[0][0]

            if message_id:
                instance.message_id_ref = message_id
                instance.save(update_fields=["message_id_ref"])
                logging.info(f"message_id_ref saved: {message_id}")
            else:
                logging.error("message_id not found in API response.")
        else:
            logging.error(f"API call failed with status: {response.status_code}, Response: {response.text}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send notification to API: {e}")
