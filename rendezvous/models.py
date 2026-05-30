from django.db import models
from patients.models import Patient
from django.utils import timezone

class RendezVous(models.Model):
    STATUT_CHOIX = [
        ('en_attente', 'En attente'),
        ('confirmé', 'Confirmé'),
        ('refusé', 'Refusé'),
        ('annulé', 'Annulé'),
        ('terminé', 'Terminé'),
    ]
    ACTION_CHOICES = [
        ('aucune', 'Aucune demande'),
        ('modification', 'Demande de modification'),
        ('annulation', 'Demande d\'annulation'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date_heure = models.DateTimeField()
    statut = models.CharField(max_length=50, choices=STATUT_CHOIX, default='en_attente')
    created_at = models.DateTimeField(auto_now_add=True)


    # Champs pour workflow patient/secrétaire
    action_patient = models.CharField(
        max_length=30, choices=ACTION_CHOICES, default='aucune',
        help_text="Action demandée par le patient (modification/annulation)."
    )
    nouvelle_date = models.DateTimeField(null=True, blank=True, help_text="Nouvelle date demandée par le patient, en attente de validation.")

    def __str__(self):
        return f"{self.patient} - {self.date_heure.strftime('%d/%m/%Y %H:%M')} - {self.statut}"

class RendezVousHistorique(models.Model):
    ACTIONS = [
        ('créé', 'Créé'),
        ('modifié', 'Modifié'),
        ('annulé', 'Annulé'),
        ('supprimé', 'Supprimé'),
        ('validé', 'Validé'),
        ('refusé', 'Refusé'),
        ('terminé', 'Terminé'),
        ('demande_modification', 'Demande de modification'),
        ('demande_annulation', 'Demande d\'annulation'),
        ('modification_validée', 'Modification validée'),
        ('annulation_validée', 'Annulation validée'),
        ('demande_refusée', 'Demande refusée'),
    ]
    rendezvous = models.ForeignKey(RendezVous, on_delete=models.CASCADE, related_name='historiques')
    action = models.CharField(max_length=50, choices=ACTIONS)
    date_action = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"Historique RDV ({self.action}) pour {self.rendezvous} à {self.date_action}"
