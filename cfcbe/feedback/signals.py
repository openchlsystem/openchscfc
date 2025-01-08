import json
import logging
import base64
import requests
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Complaint, Notification

API_URL = "http://localhost:8000/api/v1/notifications/"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sccjqsonvfvro3v2pn80iat2me",
}

@receiver(post_save, sender=Complaint)
def create_notification(sender, instance, created, **kwargs):
    if created:
        # Debug: Check initial instance state
        print(f"Signal triggered for complaint: {instance.complaint_id}, created: {created}")

        # Use transaction.on_commit to defer execution
        transaction.on_commit(lambda: generate_notification(instance))

def generate_notification(instance):
    # Explicitly refresh from database to ensure related data is included
    instance.refresh_from_db()

    # Construct victim and perpetrator details
    victim_info = (
        f"Victim: {instance.victim.name} Age: {instance.victim.age or 'N/A'}, Gender: {instance.victim.gender or 'N/A'}"
        if instance.victim else "No victim data provided."
    )
    perpetrator_info = (
        f"Perpetrator: {instance.perpetrator.name} Age: {instance.perpetrator.age or 'N/A'}, Gender: {instance.perpetrator.gender or 'N/A'})"
        if instance.perpetrator else "No perpetrator data provided."
    )

    # serialize the complaint object to json
    complaint_data = {
        "complaint_id": str(instance.complaint_id),
        "reporter_nickname": instance.reporter_nickname,
        "case_category": instance.case_category,
        "victim": {
            "name": instance.victim.name,
            "age": instance.victim.age,
            "gender": instance.victim.gender,
        },
        "perpetrator": {
            "name": instance.perpetrator.name,
            "age": instance.perpetrator.age,
            "gender": instance.perpetrator.gender,
        },
    }

    print(f"Complaint object: {complaint_data}")

    # Convert the dictionary to json
    complaint_json = json.dumps(complaint_data)
    print(f"Complaint json_data: {complaint_json}")

    # Encode the json data to base64
    encoded_data = base64.b64encode(complaint_json.encode())
    print(f"base64 data: {encoded_data}")


    # Construct the notification message
    message = (
        f"A new complaint has been filed by {instance.reporter_nickname or 'an anonymous reporter'} "
        f"in the category {instance.case_category}. {victim_info} {perpetrator_info}"
    )

    # Debug: Check the generated message
    print(f"Notification: {message}")

    # Create Notification
    Notification.objects.create(
        complaint=instance,
        message=message
    )

    # Send complaint to the API
    response = requests.post(API_URL, headers=headers, data=encoded_data)
    print(f"API Response: {response.status_code}")
    if response.status_code != 201:
        logging.error(f"Failed to send notification to API: {response.status_code}")
    else:
        logging.info(f"Notification sent to API successfully: {response.status_code}")
    
