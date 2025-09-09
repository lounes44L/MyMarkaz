"""
Script pour corriger le filtrage des classes dans main_views.py
"""
import re
import os

# Chemin du fichier à modifier
file_path = os.path.join('ecole_app', 'main_views.py')

# Lire le contenu du fichier
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Remplacer les occurrences de filtrage par classe_id par classes__id
# Utiliser une expression régulière pour cibler spécifiquement les lignes de filtrage
pattern = r'(eleves = eleves\.filter\(classe_id=classe_id\))'
replacement = r'eleves = eleves.filter(classes__id=classe_id)'

# Effectuer le remplacement
modified_content = re.sub(pattern, replacement, content)

# Écrire le contenu modifié dans le fichier
with open(file_path, 'w', encoding='utf-8') as file:
    file.write(modified_content)

print("Modifications effectuées avec succès.")
print("Les occurrences de 'eleves.filter(classe_id=classe_id)' ont été remplacées par 'eleves.filter(classes__id=classe_id)'.")
