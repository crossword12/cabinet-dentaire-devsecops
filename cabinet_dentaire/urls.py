from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', views.health_check, name='health_check'),
    path('health-page/', views.health_page, name='health_page'),
    path('', views.home, name='home'),
    path('patients/', include('patients.urls')),
    path('rendezvous/', include('rendezvous.urls')),
    path('soins/', include('soins.urls')),
    path('comptes/', include('comptes.urls')),
]

handler403 = "cabinet_dentaire.views.handler403"
