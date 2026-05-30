from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    # Redirection racine de l'app soins vers le catalogue
    path('', lambda request: redirect('liste_soins'), name='redirect_soins_root'),

    # Catalogue des types de soins
    path('catalogue/', views.liste_soins, name='liste_soins'),
    path('catalogue/ajouter/', views.ajouter_type_soin, name='ajouter_type_soin'),
    path('catalogue/<int:type_soin_id>/', views.detail_type_soin, name='detail_type_soin'),
    path('catalogue/<int:type_soin_id>/modifier/', views.modifier_type_soin, name='modifier_type_soin'),
    path('catalogue/<int:type_soin_id>/supprimer/', views.supprimer_type_soin, name='supprimer_type_soin'),

    # Soins réalisés (lecture seule, modif/suppr staff uniquement)
    path('fiche/<int:soin_id>/', views.fiche_soin, name='fiche_soin'),
    path('fiche/<int:soin_id>/modifier/', views.modifier_soin, name='modifier_soin'),
    path('fiche/<int:soin_id>/supprimer/', views.supprimer_soin, name='supprimer_soin'),

    # Espace patient : liste de ses soins
    path('mes_soins/', views.voir_mes_soins, name='voir_mes_soins'),
]
