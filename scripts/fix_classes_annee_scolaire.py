#!/usr/bin/env python
"""
Script pour associer automatiquement les classes à l'année scolaire active.
Ce script résout le problème des classes qui existent mais ne sont pas associées
à une année scolaire active, ce qui les rend invisibles dans le tableau de bord.
"""

import os
import sys
import django

# Configurer l'environnement Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_markaz.settings')
django.setup()

from ecole_app.models import Classe, AnneeScolaire, Professeur
from django.db.models import Count

def fix_classes_annee_scolaire():
    """Associe toutes les classes sans année scolaire à l'année scolaire active."""
    # Récupérer l'année scolaire active
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    
    if not annee_active:
        print("Aucune année scolaire active trouvée. Création d'une année scolaire active...")
        # Créer une année scolaire active si aucune n'existe
        from datetime import date
        annee_active = AnneeScolaire.objects.create(
            nom=f"Année {date.today().year}-{date.today().year + 1}",
            date_debut=date(date.today().year, 9, 1),
            date_fin=date(date.today().year + 1, 8, 31),
            active=True
        )
        print(f"Année scolaire active créée: {annee_active.nom}")
    
    # Récupérer toutes les classes sans année scolaire
    classes_sans_annee = Classe.objects.filter(annee_scolaire__isnull=True)
    count_sans_annee = classes_sans_annee.count()
    
    # Associer ces classes à l'année scolaire active
    classes_sans_annee.update(annee_scolaire=annee_active)
    
    print(f"{count_sans_annee} classes ont été associées à l'année scolaire active '{annee_active.nom}'")
    
    # Statistiques par professeur
    professeurs = Professeur.objects.annotate(nb_classes=Count('classes'))
    print("\nStatistiques par professeur:")
    for prof in professeurs:
        classes_prof = prof.classes.all()
        classes_avec_annee = classes_prof.filter(annee_scolaire=annee_active)
        print(f"- {prof.nom}: {classes_avec_annee.count()}/{classes_prof.count()} classes associées à l'année active")

if __name__ == "__main__":
    print("Début de la correction des classes sans année scolaire...")
    fix_classes_annee_scolaire()
    print("Opération terminée avec succès!")
