from django import forms
from .models import RendezVous
from patients.models import Patient
from django.utils import timezone
from soins.models import TypeSoin

class RendezVousForm(forms.ModelForm):
    type_soin = forms.ModelChoiceField(
        queryset=TypeSoin.objects.all(),
        label="Type de soin",
        required=True
    )

    class Meta:
        model = RendezVous
        fields = ['patient', 'date_heure', 'type_soin']
        widgets = {
            'date_heure': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.user = user

        if user and hasattr(user, 'profile'):
            if user.profile.role == 'patient':
                self.fields['patient'].widget = forms.HiddenInput()
                self.fields['patient'].initial = user.patient.pk
            else:
                self.fields['patient'].queryset = Patient.objects.all()
                self.fields['patient'].label = "Patient"

    def clean(self):
        cleaned_data = super().clean()
        patient = cleaned_data.get("patient")
        date_heure = cleaned_data.get("date_heure")

        if date_heure and date_heure < timezone.now():
            raise forms.ValidationError("La date du rendez-vous doit être dans le futur.")

        # Un patient ne peut pas avoir 2 RDV au même créneau
        if patient and date_heure:
            qs = RendezVous.objects.filter(patient=patient, date_heure=date_heure)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Ce patient a déjà un rendez-vous à ce créneau.")

            conflit_global = RendezVous.objects.filter(
                date_heure=date_heure,
                statut__in=['confirmé', 'en_attente']
            ).exclude(pk=self.instance.pk)
            if conflit_global.exists():
                raise forms.ValidationError("Un autre rendez-vous est déjà planifié à ce créneau.")

        return cleaned_data
