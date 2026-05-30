from django.urls import path
from . import views

urlpatterns = [
    # Listes
    path('tous/', views.liste_rendezvous, name='liste_rendezvous'),
    path('mes/', views.mes_rendezvous, name='mes_rendezvous'),

    # Création
    path('ajouter/', views.ajouter_rendezvous, name='ajouter_rendezvous'),
    path('demander/', views.demander_rendezvous, name='demander_rendezvous'),

    # Détail
    path('<int:pk>/', views.voir_rendezvous, name='voir_rendezvous'),

    # Modification & suppression
    path('<int:pk>/modifier/', views.modifier_rendezvous, name='modifier_rendezvous'),
    path('<int:pk>/supprimer/', views.supprimer_rendezvous, name='supprimer_rendezvous'),

    # Demandes patient
    path('<int:pk>/demande-modification/', views.demander_modification_rendezvous, name='demander_modification_rendezvous'),
    path('<int:pk>/demande-annulation/', views.demander_annulation_rendezvous, name='demander_annulation_rendezvous'),

    # Validation/refus secrétaire
    path('<int:pk>/valider-modification/', views.valider_modification_rendezvous, name='valider_modification_rendezvous'),
    path('<int:pk>/valider-annulation/', views.valider_annulation_rendezvous, name='valider_annulation_rendezvous'),
    path('<int:pk>/refuser-demande/', views.refuser_demande_rendezvous, name='refuser_demande_rendezvous'),

    path('valider/<int:pk>/', views.valider_rendezvous, name='valider_rendezvous'),
    path('refuser/<int:pk>/', views.refuser_rendezvous, name='refuser_rendezvous'),
    path('annuler/<int:pk>/', views.annuler_rendezvous, name='annuler_rendezvous'),
    path('terminer/<int:pk>/', views.terminer_rendezvous, name='terminer_rendezvous'),
]