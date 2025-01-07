from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Complaint, Notification

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

    # Debug: Check related data after refresh
    print(f"After refresh: Victim - {instance.victim}, Perpetrator - {instance.perpetrator}")

    # Construct victim and perpetrator details
    victim_info = (
        f"Victim: {instance.victim.name} (Age: {instance.victim.age or 'N/A'}, Gender: {instance.victim.gender or 'N/A'})"
        if instance.victim else "No victim data provided."
    )
    perpetrator_info = (
        f"Perpetrator: {instance.perpetrator.name} (Age: {instance.perpetrator.age or 'N/A'}, Gender: {instance.perpetrator.gender or 'N/A'})"
        if instance.perpetrator else "No perpetrator data provided."
    )

    # Construct the notification message
    message = (
        f"A new complaint has been filed by {instance.reporter_nickname or 'an anonymous reporter'} "
        f"in the category {instance.case_category}. {victim_info} {perpetrator_info}"
    )

    # Debug: Check the generated message
    print(f"Generated message: {message}")

    # Create Notification
    Notification.objects.create(
        complaint=instance,
        message=message
    )
