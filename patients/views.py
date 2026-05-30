from django.shortcuts import render, get_object_or_404, redirect
from .models import Patient
from .forms import PatientCreateForm, PatientUpdateForm, PatientSelfUpdateForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib.auth.models import User
from comptes.models import Profile
from comptes.permissions import is_secretaire, is_secretaire_or_dentiste, is_patient

@login_required
@user_passes_test(is_secretaire_or_dentiste)
def liste_patients(request):
    search = request.GET.get('search', '')
    patients = Patient.objects.all()
    if search:
        patients = patients.filter(
            Q(nom__icontains=search) | Q(prenom__icontains=search) | Q(email__icontains=search)
        )
    patients = patients.order_by("id")
    paginator = Paginator(patients, 10)
    page_number = request.GET.get('page')
    patients_page = paginator.get_page(page_number)
    return render(request, 'patients/liste_patients.html', {'patients': patients_page})

@login_required
@user_passes_test(is_secretaire)
def ajouter_patient(request):
    if request.method == 'POST':
        form = PatientCreateForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']

            # Vérification unicité username/email côté User
            if User.objects.filter(username=username).exists():
                form.add_error('username', "Ce nom d'utilisateur existe déjà.")
            elif User.objects.filter(email=email).exists():
                form.add_error('email', "Cet email est déjà utilisé.")
            else:
                # Création du User
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=form.cleaned_data.get('prenom', ''),
                    last_name=form.cleaned_data.get('nom', '')
                )

                # Création du profile
                Profile.objects.create(user=user, role='patient')

                # Création du Patient
                patient = form.save(commit=False)
                patient.user = user
                patient.save()

                messages.success(request, "Le patient a été ajouté avec succès.")
                return redirect('liste_patients')
    else:
        form = PatientCreateForm()
    return render(request, 'patients/ajouter_patient.html', {'form': form})

@login_required
def voir_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    user = request.user

    # Autoriser la secrétaire et le dentiste à voir toutes les fiches patients
    if is_secretaire_or_dentiste(user):
        autorise = True

    # Autoriser le patient uniquement à voir sa propre fiche
    elif is_patient(user) and hasattr(user, 'patient') and patient == user.patient:
        autorise = True

    # Bloquer tous les autres cas
    else:
        autorise = False

    if not autorise:
        raise PermissionDenied

    rdvs_qs = (
        patient.rendezvous_set
        .select_related('soin', 'soin__type_soin', 'soin__dentiste')
        .order_by('-date_heure')
    )

    paginator = Paginator(rdvs_qs, 8)
    page_number = request.GET.get('page')
    rdvs_page = paginator.get_page(page_number)

    return render(request, 'patients/voir_patient.html', {
        'patient': patient,
        'rdvs': rdvs_page,
    })


@login_required
@user_passes_test(is_secretaire_or_dentiste)
def modifier_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientUpdateForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Le patient a été modifié avec succès.")
            return redirect('liste_patients')
    else:
        form = PatientUpdateForm(instance=patient)
    return render(request, 'patients/modifier_patient.html', {'form': form, 'patient': patient})

@login_required
@user_passes_test(is_secretaire)
@require_POST
def supprimer_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    patient.delete()
    messages.success(request, "Le patient a été supprimé avec succès.")
    return redirect('liste_patients')

@login_required
def modifier_mon_profil(request):
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        return redirect('dashboard')
    if request.method == 'POST':
        form = PatientSelfUpdateForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect('dashboard')
    else:
        form = PatientSelfUpdateForm(instance=patient)
    return render(request, 'patients/modifier_mon_profil.html', {'form': form})

@login_required
def voir_mon_profil(request):
    try:
        patient = request.user.patient
    except ObjectDoesNotExist:
        messages.error(request, "Aucun profil patient trouvé.")
        return redirect('dashboard')

    rdvs_qs = (
        patient.rendezvous_set
        .select_related('soin', 'soin__type_soin', 'soin__dentiste')
        .order_by('-date_heure')
    )
    paginator = Paginator(rdvs_qs, 8)
    page_number = request.GET.get('page')
    rdvs_page = paginator.get_page(page_number)

    return render(request, "patients/voir_mon_profil.html", {
        'patient': patient,
        'rdvs': rdvs_page,
    })
