import os
import django

def run():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_markaz.settings')
    django.setup()
    
    # Créer les tables manquantes directement via les modèles
    from django.db import connection
    from django.db.utils import ProgrammingError
    from django.core.management import call_command
    
    print("Tentative de création des tables manquantes...")
    
    try:
        # Essayer de créer les tables manquantes
        call_command('migrate', 'ecole_app', '0041_progressioncoran', fake=True)
        call_command('migrate')
        print("Migrations appliquées avec succès!")
    except Exception as e:
        print(f"Erreur lors de l'application des migrations: {e}")
        print("Tentative de création manuelle des tables...")
        
        with connection.cursor() as cursor:
            try:
                # Création manuelle de la table siteconfig si elle n'existe pas
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ecole_app_siteconfig (
                        id SERIAL PRIMARY KEY,
                        key VARCHAR(255) NOT NULL UNIQUE,
                        value TEXT NOT NULL
                    )
                """)
                print("Table ecole_app_siteconfig créée avec succès!")
            except Exception as e:
                print(f"Erreur lors de la création de la table: {e}")

if __name__ == "__main__":
    run()
