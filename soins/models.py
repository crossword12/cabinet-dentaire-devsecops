from django.db import models
from patients.models import Patient
from django.contrib.auth.models import User  # Ou ton modèle personnalisé
from rendezvous.models import RendezVous

class TypeSoin(models.Model):
    nom = models.CharField("Nom du soin", max_length=120)
    description = models.TextField("Description", blank=True)
    tarif = models.DecimalField("Tarif (€)", max_digits=7, decimal_places=2)
    taux_remboursement = models.PositiveSmallIntegerField("Taux de remboursement (%)", default=0)

    def __str__(self):
        return f"{self.nom} ({self.tarif} € - {self.taux_remboursement}% remboursé)"

class Soin(models.Model):
    STATUT_CHOIX = [
        ('en_attente', 'En attente de validation'),
        ('validé', 'Validé'),
        ('refusé', 'Refusé'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='soins')
    type_soin = models.ForeignKey(TypeSoin, on_delete=models.PROTECT, related_name='soins_realises')
    dentiste = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'profile__role': 'dentiste'}
    )
    notes = models.TextField("Notes / Observations", blank=True)
    statut = models.CharField("Statut", max_length=20, choices=STATUT_CHOIX, default='en_attente')
    created_at = models.DateTimeField(auto_now_add=True)
    # Lien OBLIGATOIRE au rendez-vous
    rendezvous = models.OneToOneField(
        RendezVous,
        on_delete=models.CASCADE,
        related_name='soin',
        verbose_name="Rendez-vous associé"
    )

    def __str__(self):
        return f"{self.type_soin.nom} pour {self.patient} ({self.rendezvous.date_heure.strftime('%d/%m/%Y %H:%M')})"
    
    def tarif(self):
        return self.type_soin.tarif
    
    def taux_remboursement(self):
        return self.type_soin.taux_remboursement

    def montant_rembourse(self):
        return round(float(self.type_soin.tarif) * float(self.type_soin.taux_remboursement) / 100, 2)
