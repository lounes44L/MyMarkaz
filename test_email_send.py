import os
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_markaz.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("Test d'envoi d'email avec la configuration suivante:")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
# EMAIL_USE_TLS n'est pas nécessaire car nous utilisons SSL
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print("Tentative d'envoi...")

try:
    result = send_mail(
        'Test de configuration email',
        'Ceci est un test d\'envoi d\'email avec la nouvelle configuration SSL.',
        settings.DEFAULT_FROM_EMAIL,
        ['lalaouilounes2@gmail.com'],
        fail_silently=False,
    )
    print(f"Email envoyé avec succès! Résultat: {result}")
except Exception as e:
    print(f"Erreur lors de l'envoi de l'email: {str(e)}")
    import traceback
    traceback.print_exc()
