from django.db import models
from .models_ecole import Ecole

# Ajout du champ ecole aux modèles principaux
class EcoleModelMixin(models.Model):
    """
    Mixin à utiliser pour tous les modèles qui doivent être isolés par école
    """
    ecole = models.ForeignKey(Ecole, on_delete=models.CASCADE, related_name="%(class)ss", null=True)
    
    class Meta:
        abstract = True
