#!/usr/bin/env python
"""
Script pour importer les données vers Cloudflare D1
"""
import os
import sys
import json
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Charger la configuration D1
import env_config

class CloudflareD1Importer:
    def __init__(self):
        self.account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
        self.database_id = os.getenv('CLOUDFLARE_DATABASE_ID')
        self.api_token = os.getenv('CLOUDFLARE_API_TOKEN')
        
        if not all([self.account_id, self.database_id, self.api_token]):
            raise ValueError("Configuration Cloudflare D1 manquante dans .env")
        
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/d1/database/{self.database_id}"
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def execute_sql(self, sql_statements):
        """Exécute des requêtes SQL sur D1"""
        if isinstance(sql_statements, str):
            sql_statements = [sql_statements]
        
        for sql in sql_statements:
            if not sql.strip():
                continue
                
            data = {'sql': sql}
            
            response = requests.post(
                f"{self.base_url}/query",
                headers=self.headers,
                json=data
            )
            
            # Afficher la requête et la réponse complète pour debug
            print("\n=== SQL ===\n", sql)
            print("--- Réponse Cloudflare D1 ---")
            print(response.text)
            
            if response.status_code != 200:
                print(f"Erreur SQL: {sql[:100]}...")
                print(f"Réponse: {response.text}")
                return False
            
            result = response.json()
            if not result.get('success', False):
                print(f"Erreur D1: {result}")
                return False
        
        return True
    
    def execute_schema_file(self, filename):
        """Exécute un fichier de schéma SQL"""
        schema_file = BASE_DIR / filename
        
        if not schema_file.exists():
            print(f"Fichier de schéma non trouvé: {schema_file}")
            return False
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Supprimer les instructions de transaction non supportées par D1
        schema_sql = schema_sql.replace('BEGIN;', '')
        schema_sql = schema_sql.replace('COMMIT;', '')
        
        # Diviser en requêtes individuelles et filtrer les vides
        all_statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
        
        return self.execute_sql(all_statements)
    
    def create_tables_from_schema(self, schema_file):
        """Crée les tables à partir du fichier de schéma"""
        print("Création des tables dans Cloudflare D1...")
        if not self.execute_schema_file("schema_export_d1.sql"):
            print("❌ Erreur lors de la création des tables")
            return

        print("Création des index après les tables...")
        if not self.execute_schema_file("schema_export_d1_indexes.sql"):
            print("❌ Erreur lors de la création des index")
            return
        
        return True
        # Séparer les CREATE TABLE des autres requêtes
    
    def import_data_from_json(self, json_file):
        """Importe les données depuis le fichier JSON"""
        print("Importation des données...")
        
        if not json_file.exists():
            print(f"Fichier de données non trouvé: {json_file}")
            return False
        
        with open(json_file, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        
        for model_name, records in all_data.items():
            if not records:
                continue
                
            print(f"Importation de {model_name}: {len(records)} enregistrements")
            
            # Extraire le nom de la table
            table_name = model_name.split('.')[-1]
            
            for record in records:
                fields = record['fields']
                
                # Construire la requête INSERT
                columns = list(fields.keys())
                values = list(fields.values())
                
                # Ajouter l'ID si présent
                if 'pk' in record:
                    columns.insert(0, 'id')
                    values.insert(0, record['pk'])
                
                placeholders = ', '.join(['?' for _ in values])
                columns_str = ', '.join(columns)
                
                sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                
                # Exécuter avec les paramètres
                data = {
                    'sql': sql,
                    'params': values
                }
                
                response = requests.post(
                    f"{self.base_url}/query",
                    headers=self.headers,
                    json=data
                )
                
                if response.status_code != 200:
                    print(f"Erreur insertion dans {table_name}: {response.text}")
                    continue
        
        return True
    
    def test_connection(self):
        """Test la connexion à D1"""
        print("Test de connexion à Cloudflare D1...")
        
        test_sql = "SELECT 1 as test"
        result = self.execute_sql(test_sql)
        
        if result:
            print("✅ Connexion D1 réussie")
        else:
            print("❌ Échec de connexion D1")
        
        return result

def main():
    print("=== Import vers Cloudflare D1 ===")
    
    try:
        importer = CloudflareD1Importer()
        
        # Test de connexion
        if not importer.test_connection():
            print("Impossible de se connecter à D1. Vérifiez votre configuration.")
            return
        
        # Fichiers d'export
        schema_file = BASE_DIR / 'schema_export.sql'
        data_file = BASE_DIR / 'data_export.json'
        
        # Créer les tables
        if schema_file.exists():
            if importer.create_tables_from_schema(schema_file):
                print("✅ Tables créées avec succès")
            else:
                print("❌ Erreur lors de la création des tables")
                return
        
        # Importer les données
        if data_file.exists():
            if importer.import_data_from_json(data_file):
                print("✅ Données importées avec succès")
            else:
                print("❌ Erreur lors de l'importation des données")
        
        print("\n=== Import terminé ===")
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == '__main__':
    main()
