def is_secretaire(user):
    return hasattr(user, 'profile') and user.profile.role == 'secretaire'

def is_dentiste(user):
    return hasattr(user, 'profile') and user.profile.role == 'dentiste'

def is_secretaire_or_dentiste(user):
    return is_secretaire(user) or is_dentiste(user)

def is_patient(user):
    return hasattr(user, 'profile') and user.profile.role == 'patient'
