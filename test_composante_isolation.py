#!/usr/bin/env python
"""
Script de test pour vérifier l'isolation des données par composante.
Ce script va:
1. Créer une nouvelle composante
2. Vérifier qu'elle ne contient aucune donnée (élèves, professeurs, classes, etc.)
3. Ajouter quelques données à cette composante
4. Vérifier que ces données sont bien associées à cette composante uniquement
"""

import os
import sys
import django

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_markaz.settings')
django.setup()

from django.db.models import Count
from ecole_app.models import Composante, Eleve, Professeur, Classe, Creneau, Paiement, AnneeScolaire

def test_composante_isolation():
    print("\n=== TEST D'ISOLATION DES DONNÉES PAR COMPOSANTE ===\n")
    
    # 1. Créer une nouvelle composante de test
    nom_test = "Composante de Test"
    composante_test, created = Composante.objects.get_or_create(
        nom=nom_test,
        defaults={
            'description': "Composante créée pour tester l'isolation des données",
            'active': True
        }
    )
    
    if created:
        print(f"✅ Nouvelle composante créée: {composante_test}")
    else:
        print(f"ℹ️ Composante existante utilisée: {composante_test}")
        
    # 2. Vérifier que cette composante ne contient aucune donnée
    eleves_count = Eleve.objects.filter(composante=composante_test).count()
    profs_count = Professeur.objects.filter(composante=composante_test).count()
    classes_count = Classe.objects.filter(composante=composante_test).count()
    creneaux_count = Creneau.objects.filter(composante=composante_test).count()
    paiements_count = Paiement.objects.filter(composante=composante_test).count()
    
    print("\n--- VÉRIFICATION DE L'ISOLATION INITIALE ---")
    print(f"Élèves dans la composante: {eleves_count}")
    print(f"Professeurs dans la composante: {profs_count}")
    print(f"Classes dans la composante: {classes_count}")
    print(f"Créneaux dans la composante: {creneaux_count}")
    print(f"Paiements dans la composante: {paiements_count}")
    
    if eleves_count == 0 and profs_count == 0 and classes_count == 0 and creneaux_count == 0 and paiements_count == 0:
        print("✅ SUCCÈS: La nouvelle composante ne contient aucune donnée existante.")
    else:
        print("❌ ÉCHEC: La nouvelle composante contient déjà des données!")
    
    # 3. Ajouter des données de test à cette composante
    print("\n--- AJOUT DE DONNÉES DE TEST ---")
    
    # Créer une année scolaire pour cette composante
    annee, _ = AnneeScolaire.objects.get_or_create(
        nom="2025-2026 Test",
        defaults={
            'date_debut': '2025-09-01',
            'date_fin': '2026-06-30',
            'active': True,
            'composante': composante_test
        }
    )
    print(f"✅ Année scolaire créée: {annee}")
    
    # Créer un créneau
    creneau = Creneau.objects.create(
        nom="Créneau Test",
        jour="1",  # Lundi
        heure_debut="14:00:00",
        heure_fin="15:30:00",
        composante=composante_test
    )
    print(f"✅ Créneau créé: {creneau}")
    
    # Créer un professeur
    prof = Professeur.objects.create(
        nom="Professeur Test",
        telephone="0600000000",
        email="prof.test@example.com",
        composante=composante_test
    )
    print(f"✅ Professeur créé: {prof}")
    
    # Créer une classe
    classe = Classe.objects.create(
        nom="Classe Test",
        professeur=prof,
        creneau=creneau,
        capacite=20,
        annee_scolaire=annee,
        composante=composante_test
    )
    print(f"✅ Classe créée: {classe}")
    
    # Créer un élève
    eleve = Eleve.objects.create(
        nom="Élève",
        prenom="Test",
        classe=classe,
        creneau=creneau,
        annee_scolaire=annee,
        composante=composante_test
    )
    print(f"✅ Élève créé: {eleve}")
    
    # Créer un paiement
    paiement = Paiement.objects.create(
        eleve=eleve,
        montant=100.0,
        date="2025-09-15",
        methode="especes",
        annee_scolaire=annee,
        composante=composante_test
    )
    print(f"✅ Paiement créé: {paiement}")
    
    # 4. Vérifier que les données sont bien associées à cette composante uniquement
    print("\n--- VÉRIFICATION DE L'ISOLATION APRÈS AJOUT ---")
    
    # Compter les données par composante
    composantes = Composante.objects.annotate(
        nb_eleves=Count('eleve', distinct=True),
        nb_profs=Count('professeur', distinct=True),
        nb_classes=Count('classe', distinct=True),
        nb_creneaux=Count('creneau', distinct=True),
        nb_paiements=Count('paiement', distinct=True)
    )
    
    for comp in composantes:
        print(f"\nComposante: {comp.nom}")
        print(f"  Élèves: {comp.nb_eleves}")
        print(f"  Professeurs: {comp.nb_profs}")
        print(f"  Classes: {comp.nb_classes}")
        print(f"  Créneaux: {comp.nb_creneaux}")
        print(f"  Paiements: {comp.nb_paiements}")
    
    # Vérifier spécifiquement notre composante de test
    composante_test = composantes.get(id=composante_test.id)
    if (composante_test.nb_eleves == 1 and 
        composante_test.nb_profs == 1 and 
        composante_test.nb_classes == 1 and 
        composante_test.nb_creneaux == 1 and 
        composante_test.nb_paiements == 1):
        print("\n✅ SUCCÈS: Les données ajoutées sont bien associées uniquement à la composante de test.")
    else:
        print("\n❌ ÉCHEC: Les données ne sont pas correctement associées à la composante de test.")
    
    print("\n=== FIN DU TEST D'ISOLATION ===")

if __name__ == "__main__":
    test_composante_isolation()
