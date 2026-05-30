from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import RendezVous, RendezVousHistorique

@receiver(post_save, sender=RendezVous)
def log_rendezvous_save(sender, instance, created, **kwargs):
    action = None
    details = ""
    type_soin = instance.soin.type_soin.nom if hasattr(instance, "soin") and instance.soin else "Non spécifié"

    if created:
        action = 'créé'
        details = (
            f"RDV créé pour {instance.patient.nom} {instance.patient.prenom} le {instance.date_heure.strftime('%d/%m/%Y %H:%M')}.\n"
            f"Soin : {type_soin}\n"
            f"Statut : {instance.statut.capitalize()}"
        )
    else:
        try:
            old = RendezVous.objects.get(pk=instance.pk)
        except RendezVous.DoesNotExist:
            old = None

        # Tracage des demandes patient
        if instance.action_patient == 'modification' and old and old.action_patient != 'modification':
            action = 'demande_modification'
            details = (
                f"Demande de modification par le patient :\n"
                f"- Ancienne date : {old.date_heure.strftime('%d/%m/%Y %H:%M')}\n"
                f"- Nouvelle date demandée : {instance.nouvelle_date.strftime('%d/%m/%Y %H:%M') if instance.nouvelle_date else ''}\n"
                f"Soin : {type_soin}"
            )
        elif instance.action_patient == 'annulation' and old and old.action_patient != 'annulation':
            action = 'demande_annulation'
            details = (
                f"Demande d'annulation par le patient pour le RDV du {instance.date_heure.strftime('%d/%m/%Y %H:%M')}.\n"
                f"Soin : {type_soin}"
            )

        # Validation/refus par la secrétaire
        elif old and old.action_patient in ('modification', 'annulation') and instance.action_patient == 'aucune':
            if old.action_patient == 'modification':
                if instance.date_heure != old.date_heure:
                    action = 'modification_validée'
                    details = (
                        f"Modification validée par la secrétaire :\n"
                        f"- Ancienne date : {old.date_heure.strftime('%d/%m/%Y %H:%M')}\n"
                        f"- Nouvelle date : {instance.date_heure.strftime('%d/%m/%Y %H:%M')}\n"
                        f"Soin : {type_soin}"
                    )
                else:
                    action = 'demande_refusée'
                    details = (
                        "Demande de modification refusée par la secrétaire.\n"
                        f"Soin : {type_soin}"
                    )
            elif old.action_patient == 'annulation':
                if instance.statut == 'annulé':
                    action = 'annulation_validée'
                    details = (
                        "Annulation validée par la secrétaire.\n"
                        f"Soin : {type_soin}"
                    )
                else:
                    action = 'demande_refusée'
                    details = (
                        "Demande d'annulation refusée par la secrétaire.\n"
                        f"Soin : {type_soin}"
                    )
        # Modification "classique"
        else:
            changes = []
            if old:
                if instance.date_heure != old.date_heure:
                    changes.append(f"- Date/Heure : {old.date_heure.strftime('%d/%m/%Y %H:%M')} → {instance.date_heure.strftime('%d/%m/%Y %H:%M')}")
                if instance.statut != old.statut:
                    changes.append(f"- Statut : {old.statut.capitalize()} → {instance.statut.capitalize()}")
            action = 'modifié'
            if changes:
                details = (
                    f"RDV modifié pour {instance.patient.nom} {instance.patient.prenom} le {instance.date_heure.strftime('%d/%m/%Y %H:%M')} :\n"
                    f"Soin : {type_soin}\n"
                    + "\n".join(changes)
                )
            else:
                details = (
                    f"RDV modifié pour {instance.patient.nom} {instance.patient.prenom} le {instance.date_heure.strftime('%d/%m/%Y %H:%M')} (aucun changement détecté).\n"
                    f"Soin : {type_soin}"
                )

    if action:
        RendezVousHistorique.objects.create(
            rendezvous=instance,
            action=action,
            details=details
        )

@receiver(pre_delete, sender=RendezVous)
def log_rendezvous_delete(sender, instance, **kwargs):
    type_soin = instance.soin.type_soin.nom if hasattr(instance, "soin") and instance.soin else "Non spécifié"
    details = (
        f"RDV supprimé pour {instance.patient.nom} {instance.patient.prenom}.\n"
        f"Date/Heure : {instance.date_heure.strftime('%d/%m/%Y %H:%M')}\n"
        f"Soin : {type_soin}\n"
        f"Statut : {instance.statut.capitalize()}"
    )
    RendezVousHistorique.objects.create(
        rendezvous=instance,
        action='supprimé',
        details=details
    )
