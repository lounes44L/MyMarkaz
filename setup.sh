#!/bin/bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Collect static files
python Gestion_Markaz_Django/manage.py collectstatic --no-input

# Apply database migrations
python Gestion_Markaz_Django/manage.py migrate
