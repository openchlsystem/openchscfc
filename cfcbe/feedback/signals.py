from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Complaint, Notification

@receiver(post_save, sender=Complaint)
def create_notification(sender, instance, created, **kwargs):
    if created:
        message = f"A new complaint has been filed by {instance.reporter_nickname or 'an anonymous reporter'} " \
                  f"in the category {instance.case_category}."
        Notification.objects.create(
            complaint=instance,
            message=message
        )
