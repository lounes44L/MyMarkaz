"""
Script de test pour vérifier la connexion SMTP Gmail
"""
import smtplib
from email.mime.text import MIMEText
from django.conf import settings
import sys
import os
import django

# Configurer l'environnement Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_markaz.settings')
django.setup()

def test_smtp_connection():
    """Test la connexion SMTP avec les paramètres de settings.py"""
    print("=== Test de connexion SMTP ===")
    print(f"Serveur: {settings.EMAIL_HOST}")
    print(f"Port: {settings.EMAIL_PORT}")
    print(f"TLS: {settings.EMAIL_USE_TLS}")
    print(f"Utilisateur: {settings.EMAIL_HOST_USER}")
    
    try:
        # Établir la connexion
        print("\nÉtablissement de la connexion...")
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.set_debuglevel(1)  # Activer le débogage
        
        # Démarrer TLS si nécessaire
        if settings.EMAIL_USE_TLS:
            print("Démarrage TLS...")
            server.starttls()
        
        # Authentification
        print("Authentification...")
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        
        # Tester l'envoi d'un email simple
        print("\nTest d'envoi d'un email...")
        msg = MIMEText("Ceci est un test de connexion SMTP.")
        msg['Subject'] = 'Test SMTP Al Markaz'
        msg['From'] = settings.DEFAULT_FROM_EMAIL
        msg['To'] = settings.DEFAULT_FROM_EMAIL  # Envoi à soi-même
        
        server.sendmail(
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            msg.as_string()
        )
        
        # Fermer la connexion
        server.quit()
        print("\n✅ Test réussi! La connexion SMTP fonctionne correctement.")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur de connexion SMTP: {str(e)}")
        print("\nVérifiez les points suivants:")
        print("1. Le mot de passe d'application est-il correct?")
        print("2. L'authentification à 2 facteurs est-elle activée sur le compte Gmail?")
        print("3. Y a-t-il un blocage réseau ou pare-feu?")
        print("4. Gmail a-t-il détecté une activité suspecte?")
        return False

if __name__ == "__main__":
    print("\nDémarrage du test SMTP...")
    test_smtp_connection()
    print("\nTest terminé.")
