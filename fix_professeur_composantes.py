import os
import django

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_markaz.settings')
django.setup()

# Importer les modèles après avoir configuré l'environnement
from ecole_app.models import Professeur, Composante
from django.db.models import Count

def fix_professeur_composantes():
    """
    Cette fonction corrige les associations entre professeurs et composantes.
    Elle s'assure que chaque professeur est correctement associé à au moins une composante.
    """
    # Récupérer toutes les composantes
    composantes = list(Composante.objects.all())
    if not composantes:
        print("Aucune composante trouvée. Impossible de corriger les associations.")
        return
    
    # Composante par défaut (première composante)
    default_composante = composantes[0]
    print(f"Composante par défaut: {default_composante.id}: {default_composante.nom}")
    
    # Compter les professeurs sans composante
    profs_sans_composante = Professeur.objects.annotate(num_composantes=Count('composantes')).filter(num_composantes=0)
    print(f"Nombre de professeurs sans composante: {profs_sans_composante.count()}")
    
    # Pour chaque professeur sans composante
    for professeur in profs_sans_composante:
        print(f"Correction pour le professeur {professeur.id}: {professeur.nom}")
        # Ajouter la composante par défaut
        professeur.composantes.add(default_composante)
        print(f"  -> Ajout de la composante {default_composante.id}: {default_composante.nom}")
    
    # Vérifier le résultat
    profs_sans_composante_apres = Professeur.objects.annotate(num_composantes=Count('composantes')).filter(num_composantes=0).count()
    print(f"Nombre de professeurs sans composante après correction: {profs_sans_composante_apres}")
    
    # Afficher tous les professeurs et leurs composantes
    print("\nListe des professeurs et leurs composantes:")
    for prof in Professeur.objects.all():
        composantes_noms = [c.nom for c in prof.composantes.all()]
        print(f"- {prof.id}: {prof.nom} -> {composantes_noms}")

if __name__ == "__main__":
    fix_professeur_composantes()
