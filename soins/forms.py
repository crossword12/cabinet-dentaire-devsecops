from django import forms
from django.contrib.auth.models import User
from .models import Soin, TypeSoin

class SoinEditForm(forms.ModelForm):
    class Meta:
        model = Soin
        fields = ['notes', 'statut', 'dentiste']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Observations, détails éventuels…'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'dentiste': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'notes': "Notes / Observations",
            'statut': "Statut du soin",
            'dentiste': "Dentiste en charge",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Afficher uniquement les utilisateurs ayant le rôle dentiste
        self.fields['dentiste'].queryset = User.objects.filter(profile__role='dentiste')

        # Masquer le champ s'il n'y a qu'un seul dentiste disponible
        if self.fields['dentiste'].queryset.count() <= 1:
            self.fields['dentiste'].widget = forms.HiddenInput()

class TypeSoinForm(forms.ModelForm):
    class Meta:
        model = TypeSoin
        fields = ['nom', 'description', 'tarif', 'taux_remboursement']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Description du soin'}),
            'tarif': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'taux_remboursement': forms.NumberInput(attrs={'min': '0', 'max': '100'}),
        }
