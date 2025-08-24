from django.db import models
import csv
import os
from django.conf import settings

class Sourate:
    """Classe pour représenter une sourate et sa plage de pages"""
    def __init__(self, nom, page_debut, page_fin):
        self.nom = nom
        self.page_debut = int(page_debut)
        self.page_fin = int(page_fin)
    
    def __str__(self):
        return self.nom
    
    def get_pages(self):
        """Retourne la liste des pages de cette sourate"""
        return list(range(self.page_debut, self.page_fin + 1))

def charger_sourates():
    """Charge les sourates depuis le fichier CSV"""
    sourates = []
    csv_path = os.path.join(settings.BASE_DIR, 'Plage_de_pages_des_114_sourates.csv')
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                sourate = Sourate(
                    nom=row['Sourate'],
                    page_debut=row['Page début'],
                    page_fin=row['Page fin']
                )
                sourates.append(sourate)
    except Exception as e:
        print(f"Erreur lors du chargement des sourates: {e}")
    
    return sourates

# Liste des sourates chargée au démarrage
SOURATES = charger_sourates()

def get_sourates_choices():
    """Retourne les choix pour un champ de formulaire"""
    return [(i, sourate.nom) for i, sourate in enumerate(SOURATES)]

def get_pages_for_sourate(sourate_index):
    """Retourne les pages pour une sourate donnée"""
    try:
        sourate = SOURATES[int(sourate_index)]
        return [(page, str(page)) for page in sourate.get_pages()]
    except (IndexError, ValueError):
        return []
