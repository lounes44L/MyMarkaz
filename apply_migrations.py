import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_markaz.settings')
django.setup()

# Run migrations
from django.core.management import call_command
call_command('migrate')

print("Migrations applied successfully!")
