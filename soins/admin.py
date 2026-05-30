from django.contrib import admin
from .models import Soin, TypeSoin

@admin.register(Soin)
class SoinAdmin(admin.ModelAdmin):
    list_display = ('patient', 'type_soin', 'get_date_rdv', 'dentiste', 'statut')
    list_filter = ('statut', )  # Retire 'get_date_rdv' ici !
    search_fields = ('patient__nom', 'patient__prenom', 'type_soin__nom')

    def get_date_rdv(self, obj):
        if obj.rendezvous and obj.rendezvous.date_heure:
            return obj.rendezvous.date_heure
        return "-"
    get_date_rdv.short_description = 'Date du RDV'
    get_date_rdv.admin_order_field = 'rendezvous__date_heure'


@admin.register(TypeSoin)
class TypeSoinAdmin(admin.ModelAdmin):
    list_display = ('nom', 'tarif', 'taux_remboursement')
    search_fields = ('nom',)
