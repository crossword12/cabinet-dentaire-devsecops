from django.shortcuts import render, get_object_or_404, redirect
from .models import RendezVous, RendezVousHistorique
from .forms import RendezVousForm
from patients.models import Patient
from comptes.permissions import is_secretaire, is_patient, is_secretaire_or_dentiste
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from soins.models import Soin

# ============ LISTE DES RDV ============

@login_required
@user_passes_test(is_secretaire_or_dentiste)
def liste_rendezvous(request):
    search = request.GET.get('search', '')
    rendezvous = RendezVous.objects.select_related('patient').order_by('-date_heure')
    if search:
        rendezvous = rendezvous.filter(
            Q(patient__nom__icontains=search) |
            Q(patient__prenom__icontains=search)|
            Q(soin__type_soin__nom__icontains=search)
        )
    paginator = Paginator(rendezvous, 10)
    page_number = request.GET.get('page')
    rdvs_page = paginator.get_page(page_number)
    return render(request, 'rendezvous/liste_rendezvous.html', {'rendezvous': rdvs_page})

@login_required
@user_passes_test(is_patient)
def mes_rendezvous(request):
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        raise PermissionDenied
    rendezvous = RendezVous.objects.filter(patient=patient).order_by('-date_heure')
    paginator = Paginator(rendezvous, 10)
    page_number = request.GET.get('page')
    rdvs_page = paginator.get_page(page_number)
    return render(request, 'rendezvous/mes_rendezvous.html', {'rendezvous': rdvs_page})

# ============ AJOUT DE RDV PAR LE STAFF ============

@login_required
@user_passes_test(is_secretaire_or_dentiste)
def ajouter_rendezvous(request):
    if request.method == 'POST':
        form = RendezVousForm(request.POST, user=request.user)
        if form.is_valid():
            rdv = form.save(commit=False)
            # Vérifier que le patient est bien assigné
            rdv.patient = form.cleaned_data.get("patient")
            rdv.statut = 'confirmé'
            rdv.save()
            # Création du soin lié
            type_soin = form.cleaned_data.get('type_soin')
            Soin.objects.create(
                patient=rdv.patient,
                type_soin=type_soin,
                dentiste=None,
                statut='en_attente',
                rendezvous=rdv
            )
            RendezVousHistorique.objects.create(
                rendezvous=rdv,
                action='créé',
                details=f"Rendez-vous ajouté pour le {rdv.date_heure.strftime('%d/%m/%Y %H:%M')}, Soin : {type_soin}"
            )
            messages.success(request, "Le rendez-vous et le soin ont été ajoutés avec succès.")
            return redirect('liste_rendezvous')
    else:
        form = RendezVousForm(user=request.user)
    return render(request, 'rendezvous/ajouter_rendezvous.html', {'form': form})

# ============ DEMANDE DE RDV PAR PATIENT ============

@login_required
@user_passes_test(is_patient)
def demander_rendezvous(request):
    patient = request.user.patient 
    if request.method == 'POST':
        data = request.POST.copy()
        if not data.get('patient'):
            data['patient'] = patient.pk
        form = RendezVousForm(data, user=request.user)
        if form.is_valid():
            print("POST reçu :", request.POST)
            rdv = form.save(commit=False)
            rdv.patient = request.user.patient
            rdv.statut = 'en_attente'
            rdv.save()
            type_soin = form.cleaned_data.get('type_soin')
            Soin.objects.create(
                patient=rdv.patient,
                type_soin=type_soin,
                dentiste=None,
                statut='en_attente',
                rendezvous=rdv
            )
            RendezVousHistorique.objects.create(
                rendezvous=rdv,
                action='créé',
                details=f"Demande de rendez-vous envoyée pour le {rdv.date_heure.strftime('%d/%m/%Y %H:%M')}, Soin : {type_soin}"
            )
            messages.success(request, "Votre demande a été envoyée avec le soin associé. En attente de validation.")
            return redirect('mes_rendezvous')
        else:
            print("Erreurs du formulaire :", form.errors)
    else:
        form = RendezVousForm(user=request.user)
    return render(request, 'rendezvous/demander_rendezvous.html', {'form': form})

# ============ VUE DÉTAIL RDV ============

@login_required
def voir_rendezvous(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk)
    user = request.user
    if not (is_secretaire_or_dentiste(user) or (is_patient(user) and rdv.patient.user == user)):
        raise PermissionDenied
    historiques = rdv.historiques.all().order_by('-date_action')
    return render(request, 'rendezvous/voir_rendezvous.html', {'rdv': rdv, 'historiques': historiques})

# ============ MODIFIER / SUPPRIMER UN RDV ============

@login_required
@user_passes_test(is_secretaire_or_dentiste)
def modifier_rendezvous(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk)
    soin = getattr(rdv, 'soin', None)
    if request.method == 'POST':
        form = RendezVousForm(request.POST, instance=rdv, user=request.user)
        if form.is_valid():
            type_soin = form.cleaned_data.get('type_soin')
            patient = form.cleaned_data.get('patient') or rdv.patient
            old_date = rdv.date_heure
            old_statut = rdv.statut
            old_type_soin = soin.type_soin if soin else None
            new_rdv = form.save(commit=False)
            new_rdv.patient = patient
            # Confirme le RDV si c'était une demande en attente
            if old_statut == 'en_attente':
                new_rdv.statut = 'confirmé'
            new_rdv.save()
            # Mise à jour du soin
            if soin and type_soin and soin.type_soin != type_soin:
                soin.type_soin = type_soin
                soin.save()
            changements = []
            if old_date != new_rdv.date_heure:
                changements.append(f"Date changée de {old_date.strftime('%d/%m/%Y %H:%M')} à {new_rdv.date_heure.strftime('%d/%m/%Y %H:%M')}")
            if old_statut != new_rdv.statut:
                changements.append(f"Statut changé de {old_statut} à {new_rdv.statut}")
            if old_type_soin != type_soin:
                changements.append(f"Soin changé de {old_type_soin} à {type_soin}")
            RendezVousHistorique.objects.create(
                rendezvous=new_rdv,
                action='modifié',
                details="; ".join(changements) if changements else "Modification sans changement détecté."
            )
            messages.success(request, f"Le rendez-vous pour {new_rdv.patient.nom} {new_rdv.patient.prenom} a été modifié et validé.")
            return redirect('liste_rendezvous')
    else:
        initial = {}
        if soin:
            initial['type_soin'] = soin.type_soin
        form = RendezVousForm(instance=rdv, user=request.user, initial=initial)
    return render(request, 'rendezvous/modifier_rendezvous.html', {'form': form, 'rdv': rdv})

@login_required
@user_passes_test(is_secretaire)
@require_POST
def supprimer_rendezvous(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk)
    RendezVousHistorique.objects.create(
        rendezvous=rdv,
        action='supprimé',
        details=f"Rendez-vous supprimé pour le {rdv.date_heure.strftime('%d/%m/%Y %H:%M')}"
    )
    rdv.delete()
    messages.success(
        request,
        f"Le rendez-vous pour {rdv.patient.nom} {rdv.patient.prenom} le {rdv.date_heure.strftime('%d/%m/%Y %H:%M')} a été supprimé avec succès."
    )
    return redirect('liste_rendezvous')

# ============ PATIENT : DEMANDE MODIF / ANNULATION ============

@login_required
@user_passes_test(is_patient)
def demander_modification_rendezvous(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk, patient=request.user.patient)
    if request.method == 'POST':
        form = RendezVousForm(request.POST, instance=rdv, user=request.user)
        if form.is_valid():
            nouvelle_date = form.cleaned_data['date_heure']
            rdv.nouvelle_date = nouvelle_date
            rdv.action_patient = 'modification'
            rdv.statut = 'en_attente'
            rdv.save()
            RendezVousHistorique.objects.create(
                rendezvous=rdv,
                action='demande_modification',
                details=f"Demande de changement de date pour le {nouvelle_date.strftime('%d/%m/%Y %H:%M')}"
            )
            messages.info(request, "Votre demande de modification a été envoyée. En attente de validation.")
            return redirect('mes_rendezvous')
    else:
        form = RendezVousForm(instance=rdv, user=request.user)
    return render(request, 'rendezvous/demander_modification.html', {'form': form, 'rdv': rdv})

@login_required
@user_passes_test(is_patient)
def demander_annulation_rendezvous(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk, patient=request.user.patient)
    if request.method == 'POST':
        rdv.action_patient = 'annulation'
        rdv.statut = 'en_attente'
        rdv.save()
        RendezVousHistorique.objects.create(
            rendezvous=rdv,
            action='demande_annulation',
            details="Demande d'annulation envoyée par le patient."
        )
        messages.info(request, "Votre demande d’annulation a été envoyée. En attente de validation du secrétariat.")
        return redirect('mes_rendezvous')
    return render(request, 'rendezvous/demander_annulation.html', {'rdv': rdv})

# ============ SECRÉTAIRE : VALIDER / REFUSER DEMANDES ============

@login_required
@user_passes_test(is_secretaire)
@require_POST
def valider_modification_rendezvous(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk, action_patient='modification')
    RendezVousHistorique.objects.create(
        rendezvous=rdv,
        action='modification_validée',
        details=f"Date changée pour {rdv.nouvelle_date.strftime('%d/%m/%Y %H:%M')}"
    )
    rdv.date_heure = rdv.nouvelle_date
    rdv.nouvelle_date = None
    rdv.statut = 'confirmé'
    rdv.action_patient = 'aucune'
    rdv.save()
    messages.success(request, "Modification validée.")
    return redirect('liste_rendezvous')

@login_required
@user_passes_test(is_secretaire)
@require_POST
def valider_annulation_rendezvous(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk, action_patient='annulation')
    RendezVousHistorique.objects.create(
        rendezvous=rdv,
        action='annulation_validée',
        details="Annulation acceptée par le secrétariat"
    )
    rdv.statut = 'annulé'
    rdv.action_patient = 'aucune'
    rdv.save()
    messages.success(request, "Annulation validée.")
    return redirect('liste_rendezvous')

@login_required
@user_passes_test(is_secretaire)
@require_POST
def refuser_demande_rendezvous(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk)
    action_label = 'demande_refusée'
    if rdv.action_patient == 'modification':
        details = f"Demande de modification refusée pour {rdv.nouvelle_date.strftime('%d/%m/%Y %H:%M')}"
    elif rdv.action_patient == 'annulation':
        details = "Demande d'annulation refusée"
    else:
        details = "Demande refusée"
    RendezVousHistorique.objects.create(
        rendezvous=rdv,
        action=action_label,
        details=details
    )
    rdv.action_patient = 'aucune'
    rdv.nouvelle_date = None
    rdv.statut = 'confirmé'
    rdv.save()
    messages.info(request, "Demande refusée, le rendez-vous reste inchangé.")
    return redirect('liste_rendezvous')

# ============ VALIDATION, REFUS, ANNULATION PAR LE STAFF (EN ATTENTE) ============

@login_required
@user_passes_test(is_secretaire_or_dentiste)
@require_POST
def valider_rendezvous(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk, statut='en_attente')
    rdv.statut = 'confirmé' # ou 'confirmé'
    rdv.save()
    RendezVousHistorique.objects.create(
        rendezvous=rdv,
        action='validé',
        details=f"RDV validé pour le {rdv.date_heure.strftime('%d/%m/%Y %H:%M')}"
    )
    messages.success(request, "Le rendez-vous a été validé et confirmé.")
    return redirect('liste_rendezvous')

@login_required
@user_passes_test(is_secretaire_or_dentiste)
@require_POST
def refuser_rendezvous(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk, statut='en_attente')
    rdv.statut = 'refusé'
    rdv.save()
    RendezVousHistorique.objects.create(
        rendezvous=rdv,
        action='refusé',
        details="Demande de rendez-vous refusée par le staff."
    )
    messages.info(request, "La demande de rendez-vous a été refusée.")
    return redirect('liste_rendezvous')

@login_required
@user_passes_test(is_secretaire_or_dentiste)
@require_POST
def annuler_rendezvous(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk)
    rdv.statut = 'annulé'
    rdv.save()
    RendezVousHistorique.objects.create(
        rendezvous=rdv,
        action='annulé',
        details="Rendez-vous annulé par le staff."
    )
    messages.info(request, "Le rendez-vous a été annulé.")
    return redirect('liste_rendezvous')

@login_required
@user_passes_test(is_secretaire_or_dentiste)
@require_POST
def terminer_rendezvous(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk)

    if rdv.statut not in ['confirmé', 'en_attente']:
        messages.error(request, "Ce rendez-vous ne peut pas être marqué comme terminé.")
        return redirect('liste_rendezvous')

    rdv.statut = 'terminé'
    rdv.save()

    RendezVousHistorique.objects.create(
        rendezvous=rdv,
        action='terminé',
        details=f"Rendez-vous marqué comme terminé le {rdv.date_heure.strftime('%d/%m/%Y %H:%M')}."
    )

    messages.success(request, "Le rendez-vous a été marqué comme terminé.")
    return redirect('liste_rendezvous')