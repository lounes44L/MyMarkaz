from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Add page_debut and page_fin columns to ObjectifMensuel model'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check if columns exist first to avoid errors
            cursor.execute("PRAGMA table_info(ecole_app_objectifmensuel)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'page_debut' not in columns:
                self.stdout.write(self.style.SUCCESS('Adding page_debut column...'))
                cursor.execute("ALTER TABLE ecole_app_objectifmensuel ADD COLUMN page_debut integer NULL")
            else:
                self.stdout.write(self.style.WARNING('page_debut column already exists'))
                
            if 'page_fin' not in columns:
                self.stdout.write(self.style.SUCCESS('Adding page_fin column...'))
                cursor.execute("ALTER TABLE ecole_app_objectifmensuel ADD COLUMN page_fin integer NULL")
            else:
                self.stdout.write(self.style.WARNING('page_fin column already exists'))
            
            self.stdout.write(self.style.SUCCESS('Migration completed successfully!'))
