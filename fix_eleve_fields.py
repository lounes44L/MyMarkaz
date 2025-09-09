import sqlite3

def fix_eleve_fields():
    try:
        # Connexion à la base de données SQLite
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Vérifier si les colonnes existent déjà
        cursor.execute("PRAGMA table_info(ecole_app_eleve)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"Colonnes existantes: {columns}")
        
        # Ajouter les colonnes manquantes
        columns_to_add = []
        if 'prenom_pere' not in columns:
            columns_to_add.append(("prenom_pere", "varchar(100)"))
        if 'prenom_mere' not in columns:
            columns_to_add.append(("prenom_mere", "varchar(100)"))
        if 'telephone_secondaire' not in columns:
            columns_to_add.append(("telephone_secondaire", "varchar(20)"))
        
        # Exécuter les commandes ALTER TABLE
        for col_name, col_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE ecole_app_eleve ADD COLUMN {col_name} {col_type} NULL")
                print(f"Colonne {col_name} ajoutée avec succès")
            except sqlite3.OperationalError as e:
                print(f"Erreur lors de l'ajout de {col_name}: {e}")
        
        # Vérifier que les colonnes ont bien été ajoutées
        cursor.execute("PRAGMA table_info(ecole_app_eleve)")
        updated_columns = [col[1] for col in cursor.fetchall()]
        print(f"Colonnes après modification: {updated_columns}")
        
        # Valider les modifications
        conn.commit()
        print("Modifications enregistrées dans la base de données")
        
        # Marquer la migration comme appliquée dans django_migrations
        try:
            cursor.execute("SELECT * FROM django_migrations WHERE app='ecole_app' AND name='0046_add_parent_fields_to_eleve'")
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO django_migrations (app, name, applied) VALUES (?, ?, datetime('now'))",
                    ('ecole_app', '0046_add_parent_fields_to_eleve')
                )
                print("Migration marquée comme appliquée dans django_migrations")
            else:
                print("Migration déjà marquée comme appliquée")
            conn.commit()
        except Exception as e:
            print(f"Erreur lors de la mise à jour de django_migrations: {e}")
        
    except Exception as e:
        print(f"Erreur générale: {e}")
        return False
    finally:
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    success = fix_eleve_fields()
    print(f"Résultat de l'opération: {'Succès' if success else 'Échec'}")
