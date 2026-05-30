from django.urls import path
from . import views

urlpatterns = [
    # Patients classiques
    path('', views.liste_patients, name='liste_patients'),
    path('ajouter/', views.ajouter_patient, name='ajouter_patient'),
    path('voir/<int:pk>/', views.voir_patient, name='voir_patient'),
    path('modifier/<int:pk>/', views.modifier_patient, name='modifier_patient'),
    path('supprimer/<int:pk>/', views.supprimer_patient, name='supprimer_patient'),


    # PROFIL PATIENT
    path('mon_profil/', views.voir_mon_profil, name='voir_mon_profil'),                 # Lecture seule
    path('mon_profil/modifier/', views.modifier_mon_profil, name='modifier_mon_profil'),# Edition
]
