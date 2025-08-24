import os
import sqlite3
import sys
import django

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_markaz.settings')
django.setup()

def add_parent_fields_to_eleve():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute("PRAGMA table_info(ecole_app_eleve)")
        columns = [column[1] for column in cursor.fetchall()]
        print("Colonnes existantes:", columns)
        
        # Add prenom_pere column if it doesn't exist
        if 'prenom_pere' not in columns:
            print("Ajout de la colonne prenom_pere...")
            cursor.execute("ALTER TABLE ecole_app_eleve ADD COLUMN prenom_pere varchar(100) NULL")
            print("Colonne prenom_pere ajoutée")
        else:
            print("La colonne prenom_pere existe déjà")
            
        # Add prenom_mere column if it doesn't exist
        if 'prenom_mere' not in columns:
            print("Ajout de la colonne prenom_mere...")
            cursor.execute("ALTER TABLE ecole_app_eleve ADD COLUMN prenom_mere varchar(100) NULL")
            print("Colonne prenom_mere ajoutée")
        else:
            print("La colonne prenom_mere existe déjà")
        
        # Add telephone_secondaire column if it doesn't exist
        if 'telephone_secondaire' not in columns:
            print("Ajout de la colonne telephone_secondaire...")
            cursor.execute("ALTER TABLE ecole_app_eleve ADD COLUMN telephone_secondaire varchar(20) NULL")
            print("Colonne telephone_secondaire ajoutée")
        else:
            print("La colonne telephone_secondaire existe déjà")
        
        # Commit the changes
        conn.commit()
        print("Base de données mise à jour avec succès!")
        
        # Update Django migrations table to mark the migration as applied
        cursor.execute("SELECT * FROM django_migrations WHERE app='ecole_app' AND name='0046_add_parent_fields_to_eleve'")
        if not cursor.fetchone():
            print("Mise à jour de la table des migrations...")
            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (?, ?, datetime('now'))",
                ('ecole_app', '0046_add_parent_fields_to_eleve')
            )
            conn.commit()
            print("Migration marquée comme appliquée")
        else:
            print("La migration est déjà marquée comme appliquée")
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False
    finally:
        # Close the connection
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    success = add_parent_fields_to_eleve()
    if success:
        print("Script terminé avec succès")
    else:
        print("Le script a échoué")
        sys.exit(1)
