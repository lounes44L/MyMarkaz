import sqlite3

# Connexion à la base de données
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Vérifier si la colonne existe déjà
cursor.execute("PRAGMA table_info(ecole_app_progressioncoran)")
columns = cursor.fetchall()
column_names = [col[1] for col in columns]

# Ajouter la colonne si elle n'existe pas
if 'page_debut_sourate' not in column_names:
    try:
        cursor.execute("ALTER TABLE ecole_app_progressioncoran ADD COLUMN page_debut_sourate INTEGER DEFAULT 1 NOT NULL")
        print("Colonne 'page_debut_sourate' ajoutée avec succès.")
    except sqlite3.OperationalError as e:
        print(f"Erreur lors de l'ajout de la colonne: {e}")
else:
    print("La colonne 'page_debut_sourate' existe déjà.")

# Valider les changements et fermer la connexion
conn.commit()
conn.close()
