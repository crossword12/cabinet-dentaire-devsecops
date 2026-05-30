from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Secretaire, Dentiste

@receiver(post_save, sender=Secretaire)
def update_user_from_secretaire(sender, instance, **kwargs):
    instance.sync_to_user()

@receiver(post_save, sender=Dentiste)
def update_user_from_dentiste(sender, instance, **kwargs):
    instance.sync_to_user()
