from django.contrib import admin

# Register your models here.

from .models import Abonnement, Membre, Livre, Exemplaire, Emprunt

admin.site.register(Abonnement)
admin.site.register(Membre)
admin.site.register(Livre)
admin.site.register(Exemplaire)
admin.site.register(Emprunt)
