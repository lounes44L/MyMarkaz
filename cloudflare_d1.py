"""
Backend Django personnalisé pour Cloudflare D1
"""
import json
import requests
from django.db.backends.sqlite3.base import DatabaseWrapper as SQLiteDatabaseWrapper
from django.db.backends.sqlite3.creation import DatabaseCreation as SQLiteCreation
from django.db.backends.sqlite3.introspection import DatabaseIntrospection as SQLiteIntrospection
from django.db.backends.sqlite3.operations import DatabaseOperations as SQLiteOperations
from django.db.backends.sqlite3.schema import DatabaseSchemaEditor as SQLiteSchemaEditor
from django.core.exceptions import ImproperlyConfigured
import os
from dotenv import load_dotenv

load_dotenv()

class CloudflareD1Operations(SQLiteOperations):
    """Operations spécifiques à Cloudflare D1"""
    pass

class CloudflareD1Creation(SQLiteCreation):
    """Création de base de données pour Cloudflare D1"""
    pass

class CloudflareD1Introspection(SQLiteIntrospection):
    """Introspection pour Cloudflare D1"""
    pass

class CloudflareD1SchemaEditor(SQLiteSchemaEditor):
    """Éditeur de schéma pour Cloudflare D1"""
    pass

class CloudflareD1Client:
    """Client pour interagir avec l'API Cloudflare D1"""
    
    def __init__(self, account_id, database_id, api_token):
        self.account_id = account_id
        self.database_id = database_id
        self.api_token = api_token
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{database_id}"
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
    
    def execute_query(self, sql, params=None):
        """Exécute une requête SQL sur Cloudflare D1"""
        data = {
            'sql': sql
        }
        if params:
            data['params'] = params
            
        response = requests.post(
            f"{self.base_url}/query",
            headers=self.headers,
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"Erreur D1: {response.text}")
            
        return response.json()

class DatabaseWrapper(SQLiteDatabaseWrapper):
    """Wrapper de base de données pour Cloudflare D1"""
    
    vendor = 'cloudflare_d1'
    display_name = 'Cloudflare D1'
    
    # Classes spécialisées
    ops_class = CloudflareD1Operations
    creation_class = CloudflareD1Creation
    introspection_class = CloudflareD1Introspection
    SchemaEditorClass = CloudflareD1SchemaEditor
    
    def __init__(self, settings_dict, alias=None):
        super().__init__(settings_dict, alias)
        
        # Configuration Cloudflare D1
        self.account_id = settings_dict.get('ACCOUNT_ID')
        self.database_id = settings_dict.get('DATABASE_ID')
        self.api_token = settings_dict.get('API_TOKEN')
        
        if not all([self.account_id, self.database_id, self.api_token]):
            raise ImproperlyConfigured(
                "Configuration Cloudflare D1 incomplète. "
                "ACCOUNT_ID, DATABASE_ID et API_TOKEN sont requis."
            )
        
        self.d1_client = CloudflareD1Client(
            self.account_id, 
            self.database_id, 
            self.api_token
        )
    
    def get_connection_params(self):
        """Paramètres de connexion pour D1"""
        return {
            'account_id': self.account_id,
            'database_id': self.database_id,
            'api_token': self.api_token,
        }
    
    def get_new_connection(self, conn_params):
        """Crée une nouvelle connexion D1"""
        # Pour le développement, on utilise SQLite local
        # En production, on utilisera l'API D1
        if os.getenv('DEBUG', 'False').lower() == 'true':
            return super().get_new_connection({
                'database': ':memory:',
                'check_same_thread': False,
            })
        else:
            # Connexion D1 via API
            return self.d1_client
