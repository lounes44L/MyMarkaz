import sqlite3

def main():
    print("Début de la correction de la base de données...")
    
    # Connexion à la base de données
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Vérifier si les colonnes existent déjà
    cursor.execute("PRAGMA table_info(ecole_app_eleve)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Colonnes actuelles dans la table ecole_app_eleve: {columns}")
    
    # Ajouter les colonnes manquantes
    try:
        if 'prenom_pere' not in columns:
            print("Ajout de la colonne prenom_pere...")
            cursor.execute("ALTER TABLE ecole_app_eleve ADD COLUMN prenom_pere varchar(100) NULL")
        
        if 'prenom_mere' not in columns:
            print("Ajout de la colonne prenom_mere...")
            cursor.execute("ALTER TABLE ecole_app_eleve ADD COLUMN prenom_mere varchar(100) NULL")
        
        if 'telephone_secondaire' not in columns:
            print("Ajout de la colonne telephone_secondaire...")
            cursor.execute("ALTER TABLE ecole_app_eleve ADD COLUMN telephone_secondaire varchar(20) NULL")
        
        # Vérifier à nouveau les colonnes
        cursor.execute("PRAGMA table_info(ecole_app_eleve)")
        updated_columns = [col[1] for col in cursor.fetchall()]
        print(f"Colonnes après modification: {updated_columns}")
        
        # Valider les modifications
        conn.commit()
        print("Modifications enregistrées dans la base de données")
        
    except Exception as e:
        print(f"Erreur lors de la modification de la table: {e}")
        conn.rollback()
    
    # Fermer la connexion
    conn.close()
    print("Opération terminée")

if __name__ == "__main__":
    main()
