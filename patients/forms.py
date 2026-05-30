from django import forms
from django.contrib.auth.models import User
from .models import Patient
from cabinet_dentaire.utils import EmailUniqueFormMixin

class PatientCreateForm(EmailUniqueFormMixin, forms.ModelForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Patient
        fields = ['username', 'nom', 'prenom', 'date_naissance', 'telephone', 'email', 'adresse']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur existe déjà.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if Patient.objects.filter(email=email).exists() or User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")

        return email


class PatientUpdateForm(EmailUniqueFormMixin, forms.ModelForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    class Meta:
        model = Patient
        fields = ['username','nom', 'prenom', 'date_naissance', 'telephone', 'email', 'adresse']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.exclude(pk=self.instance.user.pk).filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur existe déjà.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if Patient.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")

        if User.objects.exclude(pk=self.instance.user.pk).filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")

        return email
    def save(self, commit=True):
        patient = super().save(commit=False)

        user = patient.user
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['prenom']
        user.last_name = self.cleaned_data['nom']

        if commit:
            user.save()
            patient.save()

        return patient
    
class PatientSelfUpdateForm(EmailUniqueFormMixin, forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['nom', 'prenom', 'date_naissance', 'telephone', 'email', 'adresse']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if Patient.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")

        if User.objects.exclude(pk=self.instance.user.pk).filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")

        return email