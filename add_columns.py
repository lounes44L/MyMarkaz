import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_markaz.settings')
django.setup()

# Now we can import and use Django models/connections
from django.db import connection

try:
    with connection.cursor() as cursor:
        # Check if columns exist first to avoid errors
        cursor.execute("PRAGMA table_info(ecole_app_objectifmensuel)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'page_debut' not in columns:
            print("Adding page_debut column...")
            cursor.execute("ALTER TABLE ecole_app_objectifmensuel ADD COLUMN page_debut integer NULL")
        else:
            print("page_debut column already exists")
            
        if 'page_fin' not in columns:
            print("Adding page_fin column...")
            cursor.execute("ALTER TABLE ecole_app_objectifmensuel ADD COLUMN page_fin integer NULL")
        else:
            print("page_fin column already exists")
        
        print("Migration completed successfully!")
        
except Exception as e:
    print(f"Error occurred: {e}")

