#!/bin/bash
# Exit on error
set -o errexit

# Change to the project directory
cd Gestion_Markaz_Django

# Install Python dependencies
pip install -r requirements.txt

# Install dependencies for psycopg2 if using PostgreSQL
# sudo apt-get update && sudo apt-get install -y python3-dev libpq-dev

# Collect static files
python manage.py collectstatic --noinput

# Apply database migrations
python manage.py migrate

# Create superuser if needed (uncomment and set your credentials)
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'password')" | python manage.py shell
