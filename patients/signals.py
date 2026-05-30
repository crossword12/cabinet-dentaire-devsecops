from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Patient

@receiver(post_save, sender=Patient)
def update_user_from_patient(sender, instance, **kwargs):
    instance.sync_to_user()
