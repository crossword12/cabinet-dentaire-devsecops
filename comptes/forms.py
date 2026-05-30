from django import forms
from django.contrib.auth.models import User
from .models import Profile, Secretaire, Dentiste
from patients.models import Patient
from cabinet_dentaire.utils import EmailUniqueFormMixin, email_is_unique

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirmation du mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="Adresse email",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    # Champs du modèle Patient
    date_naissance = forms.DateField(
        label="Date de naissance",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    telephone = forms.CharField(
        label="Téléphone",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    adresse = forms.CharField(
        label="Adresse",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email_is_unique(email):
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.create(user=user, role='patient')

            # Création du Patient avec tous les champs
            Patient.objects.create(
                user=user,
                nom=user.last_name,
                prenom=user.first_name,
                email=user.email,
                date_naissance=self.cleaned_data['date_naissance'],
                telephone=self.cleaned_data['telephone'],
                adresse=self.cleaned_data['adresse'],
            )
        return user



class SecretaireProfileForm(EmailUniqueFormMixin, forms.ModelForm):
    class Meta:
        model = Secretaire
        fields = ['nom', 'prenom', 'telephone', 'email']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class DentisteProfileForm(EmailUniqueFormMixin, forms.ModelForm):
    class Meta:
        model = Dentiste
        fields = ['nom', 'prenom', 'telephone', 'email', 'specialite']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'specialite': forms.TextInput(attrs={'class': 'form-control'}),
        }
