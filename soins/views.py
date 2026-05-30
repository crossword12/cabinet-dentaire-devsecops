from django.shortcuts import render, get_object_or_404, redirect
from .models import Soin, TypeSoin
from .forms import SoinEditForm, TypeSoinForm
from patients.models import Patient
from django.contrib.auth.decorators import login_required, user_passes_test
from comptes.permissions import is_secretaire_or_dentiste, is_patient, is_secretaire
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models.deletion import ProtectedError

# ========== MODIFICATION & SUPPRESSION DES SOINS RÉALISÉS ==========

@login_required
@user_passes_test(is_secretaire_or_dentiste)
def modifier_soin(request, soin_id):
    soin = get_object_or_404(Soin, pk=soin_id)
    if request.method == "POST":
        form = SoinEditForm(request.POST, instance=soin)
        if form.is_valid():
            form.save()
            messages.success(request, "Le soin a été modifié.")
            return redirect('fiche_soin', soin_id=soin.pk)
    else:
        form = SoinEditForm(instance=soin)
    return render(request, 'soins/modifier_soin.html', {'form': form, 'soin': soin})

@login_required
@user_passes_test(is_secretaire_or_dentiste)
def supprimer_soin(request, soin_id):
    soin = get_object_or_404(Soin, pk=soin_id)
    patient_pk = soin.patient.pk
    if request.method == "POST":
        soin.delete()
        messages.success(request, "Le soin a bien été supprimé.")
        return redirect('voir_patient', pk=patient_pk)
    return render(request, 'soins/supprimer_soin.html', {'soin': soin})

@login_required
def fiche_soin(request, soin_id):
    soin = get_object_or_404(Soin, pk=soin_id)
    user = request.user

    if is_secretaire_or_dentiste(user):
        autorise = True
    elif is_patient(user) and hasattr(user, 'patient') and soin.patient == user.patient:
        autorise = True
    else:
        autorise = False

    if not autorise:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    return render(request, 'soins/fiche_soin.html', {'soin': soin})

# ========== CATALOGUE DES TYPES DE SOINS (ADMIN & STAFF) ==========

@login_required
@user_passes_test(is_secretaire_or_dentiste)
def ajouter_type_soin(request):
    if request.method == "POST":
        form = TypeSoinForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Le soin a été ajouté au catalogue.")
            return redirect('liste_soins')
    else:
        form = TypeSoinForm()
    return render(request, 'soins/ajouter_type_soin.html', {'form': form})

@login_required
@user_passes_test(is_secretaire_or_dentiste)
def modifier_type_soin(request, type_soin_id):
    type_soin = get_object_or_404(TypeSoin, pk=type_soin_id)
    if request.method == "POST":
        form = TypeSoinForm(request.POST, instance=type_soin)
        if form.is_valid():
            form.save()
            messages.success(request, "Le soin du catalogue a été modifié.")
            return redirect('liste_soins')
    else:
        form = TypeSoinForm(instance=type_soin)
    return render(request, 'soins/modifier_type_soin.html', {'form': form, 'type_soin': type_soin})

@login_required
@user_passes_test(is_secretaire_or_dentiste)
def supprimer_type_soin(request, type_soin_id):
    type_soin = get_object_or_404(TypeSoin, pk=type_soin_id)
    if request.method == "POST":
        try:
            type_soin.delete()
            messages.success(request, "Le soin a bien été supprimé du catalogue.")
        except ProtectedError:
            messages.error(request, "Impossible de supprimer ce type de soin car il est déjà utilisé dans un soin.")
        return redirect('liste_soins')
    return render(request, 'soins/supprimer_type_soin.html', {'type_soin': type_soin})

def liste_soins(request):
    search = request.GET.get('search', '')
    soins = TypeSoin.objects.all()
    if search:
        soins = soins.filter(nom__icontains=search)
    soins = soins.order_by("id")
    paginator = Paginator(soins, 12)
    page_number = request.GET.get('page')
    soins_page = paginator.get_page(page_number)
    return render(request, 'soins/liste_soins.html', {'soins': soins_page})

def detail_type_soin(request, type_soin_id):
    type_soin = get_object_or_404(TypeSoin, pk=type_soin_id)
    return render(request, 'soins/detail_type_soin.html', {'type_soin': type_soin})

# ========== SOINS POUR LE PATIENT (LISTE EN LECTURE SEULE) ==========

@login_required
@user_passes_test(is_patient)
def voir_mes_soins(request):
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        return redirect('dashboard')
    # Les soins sont forcément liés à un rendez-vous désormais
    soins = patient.soins.select_related('type_soin', 'dentiste', 'rendezvous').order_by('-rendezvous__date_heure')
    return render(request, 'soins/voir_mes_soins.html', {'soins': soins})

# ========== FONCTIONNALITÉS SUPPRIMÉES ==========

# - PAS de création manuelle de soin par le patient (plus de 'demander_soin')
# - PAS de vue 'ajouter_soin' (création automatique lors de la création/validation du RDV)
# - PAS de validation/refus de soin isolé par secrétaire (se gère via le workflow rendez-vous)

