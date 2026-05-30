from django.db import models
from django.contrib.auth.models import User
from cabinet_dentaire.utils import UserSyncMixin, email_is_unique

class Patient(UserSyncMixin, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)
    adresse = models.CharField(max_length=255, blank=True)
    date_inscription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Patient"
