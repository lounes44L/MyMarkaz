#!/usr/bin/env python
"""
Script pour exporter les données de la base SQLite actuelle
"""
import os
import sys
import django
import json
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Charger la configuration D1
sys.path.append(str(BASE_DIR))
import env_config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_markaz.settings')
django.setup()

from django.core import serializers
from django.apps import apps

def export_all_data():
    """Exporte toutes les données des modèles Django"""
    
    # Obtenir tous les modèles de l'application ecole_app
    app_models = apps.get_app_config('ecole_app').get_models()
    
    # Dictionnaire pour stocker les données
    all_data = {}
    
    print("Exportation des données en cours...")
    
    for model in app_models:
        model_name = f"{model._meta.app_label}.{model._meta.model_name}"
        print(f"Exportation de {model_name}...")
        
        # Sérialiser tous les objets du modèle
        queryset = model.objects.all()
        serialized_data = serializers.serialize('json', queryset)
        
        # Convertir en dictionnaire Python
        data_list = json.loads(serialized_data)
        all_data[model_name] = data_list
        
        print(f"  -> {len(data_list)} enregistrements exportés")
    
    # Sauvegarder dans un fichier JSON
    export_file = BASE_DIR / 'data_export.json'
    with open(export_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\nExportation terminée ! Données sauvegardées dans : {export_file}")
    print(f"Taille du fichier : {export_file.stat().st_size / 1024:.2f} KB")
    
    return export_file

def export_to_sql():
    """Exporte les données au format SQL pour Cloudflare D1"""
    
    # Utiliser Django pour générer le dump SQL
    from django.core.management import call_command
    from io import StringIO
    
    sql_output = StringIO()
    
    # Générer le schéma SQL
    call_command('sqlmigrate', 'ecole_app', '0001', stdout=sql_output)
    
    # Sauvegarder le schéma
    schema_file = BASE_DIR / 'schema_export.sql'
    with open(schema_file, 'w', encoding='utf-8') as f:
        f.write(sql_output.getvalue())
    
    print(f"Schéma SQL exporté dans : {schema_file}")
    
    return schema_file

if __name__ == '__main__':
    print("=== Export des données MyMarkaz ===")
    
    # Export JSON
    json_file = export_all_data()
    
    # Export SQL schema
    sql_file = export_to_sql()
    
    print("\n=== Export terminé ===")
    print(f"Fichiers générés :")
    print(f"  - Données JSON : {json_file}")
    print(f"  - Schéma SQL : {sql_file}")
