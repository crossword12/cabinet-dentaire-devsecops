from django.apps import AppConfig

class RendezvousConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rendezvous'

    def ready(self):
        pass
        # Les signaux d'historique sont désactivés pour éviter les doublons.
        # L'historique est géré manuellement dans rendezvous/views.py.
        # import rendezvous.signals  # noqa