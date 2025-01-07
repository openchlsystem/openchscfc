import base64
import json
import logging
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Complaint, Notification

logger = logging.getLogger(__name__)

API_URL = "https://demo-openchs.bitz-itc.com/helpline/api/"  # Replace with the actual API endpoint
API_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sccjqsonvfvro3v2pn80iat2me"  # Replace with a valid API token
}


@receiver(post_save, sender=Complaint)
def create_notification(sender, instance, created, **kwargs):
    if created:
        # Fetch the instance with related victim and perpetrator objects
        instance = Complaint.objects.select_related('victim', 'perpetrator').get(pk=instance.pk)

        message = f"A new complaint has been filed by {instance.reporter_nickname or 'an anonymous reporter'} " \
                  f"in the category {instance.case_category}."
        try:
            Notification.objects.create(
                complaint=instance,
                message=message
            )
            print(f"Notification: {message}")
        except Exception as e:
            print(f"Error creating notification: {e}")

        # Serialize the Complaint object
        complaint_data = {
            "complaint_id": str(instance.complaint_id),
            "reporter_nickname": instance.reporter_nickname or "Anonymous",
            "case_category": instance.case_category,
            "complaint_text": instance.complaint_text,
            "complaint_audio": base64.b64encode(instance.complaint_audio).decode("utf-8") if instance.complaint_audio else None,
            "created_at": instance.created_at.isoformat(),
            "victim": {
                "name": instance.victim.name if instance.victim else None,
                "age": instance.victim.age if instance.victim else None,
                "gender": instance.victim.gender if instance.victim else None,
                "additional_info": instance.victim.additional_info if instance.victim else None,
            },
            "perpetrator": {
                "name": instance.perpetrator.name if instance.perpetrator else None,
                "age": instance.perpetrator.age if instance.perpetrator else None,
                "gender": instance.perpetrator.gender if instance.perpetrator else None,
                "additional_info": instance.perpetrator.additional_info if instance.perpetrator else None,
            }
        }

        # Convert the serialized data to JSON and then encode to Base64
        json_data = json.dumps(complaint_data)
        print(f"Complaint data: {json_data}")
        base64_data = base64.b64encode(json_data.encode("utf-8")).decode("utf-8")
        print(f"Base64 data: {base64_data}")

        # Post the Base64 data to the API
        payload = {"data": base64_data}
        try:
            response = requests.post(API_URL, json=payload, headers=API_HEADERS)
            if response.status_code == 200:
                logger.info(f"Complaint {instance.complaint_id} successfully sent to the API.")
            else:
                logger.error(f"Failed to send complaint {instance.complaint_id}. Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            logger.error(f"Error sending complaint {instance.complaint_id} to the API: {e}")
