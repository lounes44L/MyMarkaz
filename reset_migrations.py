#!/usr/bin/env python3
"""
Script to reset and recreate migrations safely
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

def create_parametresite_table():
    """Create the missing ParametreSite table"""
    with connection.cursor() as cursor:
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='ecole_app_parametresite'
        """)
        result = cursor.fetchone()
        
        if not result:
            print("Creating ParametreSite table...")
            cursor.execute("""
                CREATE TABLE ecole_app_parametresite (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    montant_defaut_eleve DECIMAL(10, 2) NOT NULL DEFAULT 200.00,
                    date_modification DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                INSERT INTO ecole_app_parametresite (montant_defaut_eleve, date_modification)
                VALUES (200.00, datetime('now'))
            """)
            print("ParametreSite table created successfully!")
            return True
        else:
            print("ParametreSite table already exists")
            return False

if __name__ == "__main__":
    create_parametresite_table()
