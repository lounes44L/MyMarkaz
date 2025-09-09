import os
import sqlite3
import sys

def add_columns_to_objectifmensuel():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute("PRAGMA table_info(ecole_app_objectifmensuel)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add page_debut column if it doesn't exist
        if 'page_debut' not in columns:
            print("Adding page_debut column...")
            cursor.execute("ALTER TABLE ecole_app_objectifmensuel ADD COLUMN page_debut integer NULL")
        else:
            print("page_debut column already exists")
            
        # Add page_fin column if it doesn't exist
        if 'page_fin' not in columns:
            print("Adding page_fin column...")
            cursor.execute("ALTER TABLE ecole_app_objectifmensuel ADD COLUMN page_fin integer NULL")
        else:
            print("page_fin column already exists")
        
        # Commit the changes
        conn.commit()
        print("Database updated successfully!")
        
        # Update Django migrations table to mark the migration as applied
        cursor.execute("SELECT * FROM django_migrations WHERE app='ecole_app' AND name='0043_add_page_fields_to_objectif'")
        if not cursor.fetchone():
            print("Updating migrations table...")
            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (?, ?, datetime('now'))",
                ('ecole_app', '0043_add_page_fields_to_objectif')
            )
            conn.commit()
            print("Migration marked as applied")
        else:
            print("Migration already marked as applied")
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        # Close the connection
        if conn:
            conn.close()
    
    return True

if __name__ == "__main__":
    success = add_columns_to_objectifmensuel()
    if success:
        print("Script completed successfully")
    else:
        print("Script failed")
        sys.exit(1)
