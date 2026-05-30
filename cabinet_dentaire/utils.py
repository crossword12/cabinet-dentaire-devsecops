from django import forms
from django.contrib.auth.models import User

def email_is_unique(email, exclude_user_id=None):
    """
    Vérifie l'unicité globale de l'email parmi tous les utilisateurs et profils (Patient, Secretaire, Dentiste).
    Utilisé dans tous les formulaires de création/modification de compte ou de profil.
    """
    email = email.lower()
    user_qs = User.objects.filter(email__iexact=email)
    if exclude_user_id:
        user_qs = user_qs.exclude(id=exclude_user_id)
    if user_qs.exists():
        return False
    # Import dynamique pour casser la boucle d'import
    from patients.models import Patient
    from comptes.models import Secretaire, Dentiste
    if Patient.objects.filter(email__iexact=email).exists():
        return False
    if Secretaire.objects.filter(email__iexact=email).exists():
        return False
    if Dentiste.objects.filter(email__iexact=email).exists():
        return False
    return True

class UserSyncMixin:
    """
    À utiliser sur tout modèle lié à User via un champ OneToOneField nommé 'user',
    ayant des champs nom, prenom, email à synchroniser.
    Appelle self.sync_to_user() après chaque .save() du profil.
    """
    def sync_to_user(self):
        self.user.first_name = self.prenom
        self.user.last_name = self.nom
        self.user.email = self.email
        self.user.save()

class EmailUniqueFormMixin:
    """
    À utiliser sur tout formulaire ModelForm qui propose l'édition d'un champ email,
    pour s'assurer de l'unicité globale.
    """
    def clean_email(self):
        email = self.cleaned_data.get('email')
        instance = getattr(self, 'instance', None)
        # Si le profil a un user lié, on l'exclut de la recherche pour éviter un faux positif
        exclude_user_id = instance.user.id if instance and getattr(instance, 'user_id', None) else None
        if not email_is_unique(email, exclude_user_id=exclude_user_id):
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email
