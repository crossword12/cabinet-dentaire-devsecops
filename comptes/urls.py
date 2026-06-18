from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('contact/', views.contact_cabinet, name='contact_cabinet'),

    # Page interdite pour /comptes/patients/
    path('patients/', views.patients_interdit, name='comptes_patients_interdit'),


    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='comptes/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),

    # PROFIL DENTISTE
    path('dentiste/profil/', views.voir_mon_profil_dentiste, name='voir_mon_profil_dentiste'),   # Lecture seule
    path('dentiste/profil/modifier/', views.mon_profil_dentiste, name='mon_profil_dentiste'),     # Edition

    # PROFIL SECRETAIRE
    path('secretaire/profil/', views.voir_mon_profil_secretaire, name='voir_mon_profil_secretaire'), # Lecture seule
    path('secretaire/profil/modifier/', views.mon_profil_secretaire, name='mon_profil_secretaire'),  # Edition

]
