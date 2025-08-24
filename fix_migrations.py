#!/usr/bin/env python3
"""
Script to fix migration conflicts and create missing ParametreSite table
"""

import os
import sys
import django

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_markaz.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def fix_database():
    """Fix database schema issues"""
    print("Fixing database migration conflicts...")
    
    # Check if ParametreSite table exists
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='ecole_app_parametresite'
        """)
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("ParametreSite table missing - creating...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ecole_app_parametresite (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    montant_defaut_eleve DECIMAL(10, 2) NOT NULL DEFAULT 200.00,
                    date_modification DATETIME NOT NULL
                )
            """)
            cursor.execute("""
                INSERT OR IGNORE INTO ecole_app_parametresite 
                (id, montant_defaut_eleve, date_modification)
                VALUES (1, 200.00, datetime('now'))
            """)
            print("ParametreSite table created successfully!")
        else:
            print("ParametreSite table already exists")

if __name__ == "__main__":
    fix_database()
    print("Database fix completed!")
