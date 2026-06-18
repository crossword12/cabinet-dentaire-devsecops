from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, SecretaireProfileForm, DentisteProfileForm
from .models import Secretaire, Dentiste
from django.utils import timezone
from rendezvous.models import RendezVous
from .models import Profile
from django.core.exceptions import PermissionDenied

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Votre compte patient a été créé. Vous pouvez vous connecter.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'comptes/register.html', {'form': form})


def contact_cabinet(request):
    # Tu peux aussi rendre cette vue accessible sans connexion si tu veux
    return render(request, 'comptes/contact_cabinet.html')

@login_required
def mon_profil_secretaire(request):
    try:
        secretaire = request.user.secretaire
    except Secretaire.DoesNotExist:
        messages.error(request, "Aucun profil secrétaire associé à ce compte.")
        return redirect('dashboard')
    if request.method == 'POST':
        form = SecretaireProfileForm(request.POST, instance=secretaire)
        if form.is_valid():
            secretaire = form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect('mon_profil_secretaire')
    else:
        form = SecretaireProfileForm(instance=secretaire)
    return render(request, 'comptes/mon_profil_secretaire.html', {'form': form})

@login_required
def voir_mon_profil_secretaire(request):
    try:
        secretaire = request.user.secretaire
    except Secretaire.DoesNotExist:
        messages.error(request, "Aucun profil secretaire associé à ce compte.")
        return redirect('dashboard')

    period = request.GET.get('period', 'futur')
    qs = RendezVous.objects.all()
    if period == 'futur':
        qs = qs.filter(date_heure__gte=timezone.now())
    rdvs = qs.order_by('date_heure')

    return render(request, 'comptes/voir_mon_profil_secretaire.html', {
        'secretaire': secretaire,
        'rdvs': rdvs,
        'selected_period': period,
    })

@login_required
def mon_profil_dentiste(request):
    try:
        dentiste = request.user.dentiste
    except Dentiste.DoesNotExist:
        messages.error(request, "Aucun profil dentiste associé à ce compte.")
        return redirect('dashboard')
    if request.method == 'POST':
        form = DentisteProfileForm(request.POST, instance=dentiste)
        if form.is_valid():
            dentiste = form.save() # Synchronisation ici
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect('mon_profil_dentiste')
    else:
        form = DentisteProfileForm(instance=dentiste)
    return render(request, 'comptes/mon_profil_dentiste.html', {'form': form})

@login_required
def voir_mon_profil_dentiste(request):
    try:
        dentiste = request.user.dentiste
    except Dentiste.DoesNotExist:
        messages.error(request, "Aucun profil dentiste associé à ce compte.")
        return redirect('dashboard')

    # Récupère le paramètre de filtrage (GET)
    period = request.GET.get('period', 'futur')  # par défaut "futur"

    # Filtrage dynamique
    qs = RendezVous.objects.all()
    if period == 'futur':
        qs = qs.filter(date_heure__gte=timezone.now())
    rdvs = qs.order_by('date_heure')

    return render(request, 'comptes/voir_mon_profil_dentiste.html', {
        'dentiste': dentiste,
        'rdvs': rdvs,
        'selected_period': period,
    })

@login_required
def dashboard(request):
    """Affiche le dashboard en fonction du rôle de l'utilisateur."""

    # Vérifier si l'utilisateur possède un profil
    if not hasattr(request.user, 'profile'):
        messages.error(request, "Aucun profil n'est associé à ce compte. Veuillez contacter l'administrateur.")
        return redirect('admin:index') if request.user.is_staff else redirect('logout')

    role = request.user.profile.role

    if role == 'secretaire':
        return render(request, 'comptes/dashboard_secretaire.html')

    elif role == 'dentiste':
        return render(request, 'comptes/dashboard_dentiste.html')

    elif role == 'patient':
        return render(request, 'comptes/dashboard_patient.html')

    messages.error(request, "Rôle utilisateur inconnu.")
    return redirect('logout')

def patients_interdit(request):
    raise PermissionDenied("Vous n’avez pas les droits pour accéder à cette page.")