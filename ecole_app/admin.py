from django.contrib import admin
from django.utils.html import format_html
from .models import Eleve, Professeur, Classe, Creneau, Paiement, ParametreSite

# Interface d'administration personnalisée

@admin.register(Creneau)
class CreneauAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date_creation', 'nombre_eleves', 'nombre_profs')
    search_fields = ('nom',)
    
    def nombre_eleves(self, obj):
        return obj.eleves.count()
    nombre_eleves.short_description = "Nombre d'élèves"
    
    def nombre_profs(self, obj):
        return obj.professeurs.count()
    nombre_profs.short_description = "Nombre de professeurs"

@admin.register(ParametreSite)
class ParametreSiteAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'montant_defaut_eleve', 'date_modification')
    fieldsets = (
        ('Paramètres financiers', {
            'fields': ('montant_defaut_eleve',)
        }),
    )
    
    def has_add_permission(self, request):
        # Empêcher la création de plusieurs instances
        return not ParametreSite.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Empêcher la suppression
        return False

@admin.register(Professeur)
class ProfesseurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'creneaux_list', 'nombre_classes', 'date_creation')
    list_filter = ()
    search_fields = ('nom',)

    def creneaux_list(self, obj):
        return ", ".join([str(c) for c in obj.creneaux.all()])
    creneaux_list.short_description = "Créneaux"    
    def nombre_classes(self, obj):
        return obj.classes.count()
    nombre_classes.short_description = "Nombre de classes"

@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ('nom', 'professeur', 'creneau', 'capacite', 'nombre_eleves', 'taux_occupation_display')
    list_filter = ('creneau', 'professeur')
    search_fields = ('nom',)
    
    def nombre_eleves(self, obj):
        return obj.eleves.count()
    nombre_eleves.short_description = "Nombre d'élèves"
    
    def taux_occupation_display(self, obj):
        taux = obj.taux_occupation()
        color = 'green'
        if taux > 85:
            color = 'red'
        elif taux > 60:
            color = 'orange'
        return format_html('<span style="color: {}; font-weight: bold;">{} %</span>', color, taux)
    taux_occupation_display.short_description = "Taux d'occupation"

@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    list_display = ('nom_complet', 'classe', 'creneaux_list', 'telephone', 'email', 'date_creation')
    list_filter = ('classe',)
    search_fields = ('nom', 'prenom', 'telephone', 'email')
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'date_naissance', 'telephone', 'email')
        }),
        ('Informations scolaires', {
            'fields': ('classe', 'creneaux')
        }),
        ('Adresse', {
            'fields': ('adresse',),
            'classes': ('collapse',)
        }),
    )
    
    def nom_complet(self, obj):
        return f"{obj.nom} {obj.prenom}".strip()
    nom_complet.short_description = "Nom complet"

    def creneaux_list(self, obj):
        return ", ".join([str(c) for c in obj.creneaux.all()])
    creneaux_list.short_description = "Créneaux"

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'montant', 'methode', 'date', 'date_creation')
    list_filter = ('methode', 'date')
    search_fields = ('eleve__nom', 'eleve__prenom', 'commentaire')
    date_hierarchy = 'date'
