import os
import django

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_markaz.settings')
django.setup()

# Importer les modèles après avoir configuré l'environnement
from ecole_app.models import Professeur, Composante
from django.db.models import Count

def fix_all_professeurs():
    """
    Cette fonction associe tous les professeurs à toutes les composantes.
    """
    # Récupérer tous les professeurs et toutes les composantes
    professeurs = Professeur.objects.all()
    composantes = Composante.objects.all()
    
    print(f"Nombre de professeurs: {professeurs.count()}")
    print(f"Nombre de composantes: {composantes.count()}")
    
    # Pour chaque professeur, l'associer à toutes les composantes
    for professeur in professeurs:
        print(f"Traitement du professeur {professeur.id}: {professeur.nom}")
        
        # Afficher les composantes actuelles
        composantes_actuelles = [c.nom for c in professeur.composantes.all()]
        print(f"  Composantes actuelles: {composantes_actuelles}")
        
        # Associer à toutes les composantes
        for composante in composantes:
            professeur.composantes.add(composante)
            print(f"  -> Ajout de la composante {composante.id}: {composante.nom}")
        
        # Vérifier le résultat
        composantes_apres = [c.nom for c in professeur.composantes.all()]
        print(f"  Composantes après correction: {composantes_apres}")
    
    print("\nOpération terminée.")

if __name__ == "__main__":
    fix_all_professeurs()
