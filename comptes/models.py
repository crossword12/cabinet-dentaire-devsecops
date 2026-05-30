from django.db import models
from django.contrib.auth.models import User
from cabinet_dentaire.utils import UserSyncMixin

class Profile(models.Model):
    ROLES = (
        ('secretaire', 'Secrétaire'),
        ('dentiste', 'Dentiste'),
        ('patient', 'Patient'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Secretaire(UserSyncMixin, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='secretaire')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.nom} {self.prenom}"

class Dentiste(UserSyncMixin, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dentiste')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)
    specialite = models.CharField(max_length=100, blank=True)  # optionnel

    def __str__(self):
        return f"{self.nom} {self.prenom}"
