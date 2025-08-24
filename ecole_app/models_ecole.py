from django.db import models
from django.contrib.auth.models import User

class Ecole(models.Model):
    """
    Modèle représentant une école utilisant l'application.
    Chaque école a son propre administrateur et ses propres données isolées.
    """
    nom = models.CharField(max_length=200, help_text="Nom de l'école")
    adresse = models.TextField(blank=True, null=True, help_text="Adresse de l'école")
    telephone = models.CharField(max_length=20, blank=True, null=True, help_text="Numéro de téléphone de l'école")
    email = models.EmailField(blank=True, null=True, help_text="Email de contact de l'école")
    site_web = models.URLField(blank=True, null=True, help_text="Site web de l'école")
    logo = models.ImageField(upload_to='logos_ecoles/', blank=True, null=True, help_text="Logo de l'école")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    # Relation avec l'utilisateur administrateur de l'école
    admin = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ecole_admin')
    
    # Paramètres de personnalisation
    couleur_primaire = models.CharField(max_length=7, default="#007bff", help_text="Couleur primaire pour la personnalisation (format hex: #RRGGBB)")
    couleur_secondaire = models.CharField(max_length=7, default="#6c757d", help_text="Couleur secondaire pour la personnalisation (format hex: #RRGGBB)")
    
    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name = "École"
        verbose_name_plural = "Écoles"
