"""
Script de test pour vérifier la génération des identifiants et mots de passe des élèves
"""
import os
import django

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_markaz.settings')
django.setup()

from django.contrib.auth.models import User
from ecole_app.models import Eleve, Composante

# Créer une composante de test si nécessaire
composante, created = Composante.objects.get_or_create(nom="Test Composante")

# Supprimer l'élève de test s'il existe déjà
User.objects.filter(username__startswith="dupont.jean").delete()
Eleve.objects.filter(nom="Dupont", prenom="Jean").delete()

# Créer un nouvel élève
eleve = Eleve.objects.create(
    nom="Dupont",
    prenom="Jean",
    composante=composante
)

# Récupérer l'élève avec son utilisateur (après que le signal ait été exécuté)
eleve = Eleve.objects.get(id=eleve.id)

# Afficher les informations de l'utilisateur
print(f"Élève créé: {eleve.nom} {eleve.prenom}")
print(f"Identifiant: {eleve.user.username}")
print(f"Mot de passe: {eleve.mot_de_passe_en_clair}")

# Tester avec des caractères spéciaux
User.objects.filter(username__startswith="dupontmartin").delete()
Eleve.objects.filter(nom="Dupont-Martin", prenom="Jean-Pierre").delete()

eleve_special = Eleve.objects.create(
    nom="Dupont-Martin",
    prenom="Jean-Pierre",
    composante=composante
)

eleve_special = Eleve.objects.get(id=eleve_special.id)
print("\nÉlève avec caractères spéciaux:")
print(f"Élève créé: {eleve_special.nom} {eleve_special.prenom}")
print(f"Identifiant: {eleve_special.user.username}")
print(f"Mot de passe: {eleve_special.mot_de_passe_en_clair}")
