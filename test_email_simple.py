import os
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_markaz.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

try:
    # Test d'envoi d'email simple
    send_mail(
        'Test d\'envoi d\'email',
        'Ceci est un test d\'envoi d\'email depuis Django.',
        settings.DEFAULT_FROM_EMAIL,
        ['lalaouilounes2@gmail.com'],
        fail_silently=False,
    )
    print("Email envoyé avec succès!")
except Exception as e:
    print(f"Erreur lors de l'envoi de l'email: {str(e)}")
    
    # Afficher la configuration email actuelle
    print("\nConfiguration email actuelle:")
    print(f"EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'Non défini')}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Non défini')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Non défini')}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Non défini')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Non défini')}")
    print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Non défini')}")
