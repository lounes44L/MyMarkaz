"""
Utilitaire de débogage pour l'envoi d'emails
Ce fichier permet de tester la configuration email et d'afficher des messages détaillés
"""

import os
import logging
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives

def test_email_config():
    """Test la configuration email"""
    print("=== Configuration Email ===")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    # Test d'envoi simple
    try:
        send_mail(
            'Test Email',
            'Ceci est un email de test.',
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],  # Envoyer à soi-même pour tester
            fail_silently=False,
        )
        print("✅ Email de test envoyé avec succès!")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi: {e}")
        return False

def send_credentials_debug(to_email, username, password, user_type="professeur"):
    """Envoie les identifiants avec journalisation détaillée"""
    
    subject = f"Vos identifiants de connexion - École Al Markaz ({user_type})"
    message = f"""
    Bonjour,

    Voici vos identifiants de connexion pour votre compte École Al Markaz :

    Identifiant: {username}
    Mot de passe: {password}

    Veuillez conserver ces informations en lieu sûr.

    Cordialement,
    L'équipe de gestion de l'École Al Markaz
    """
    
    html_message = f"""
    <html>
    <body>
        <h2>École Al Markaz - Vos identifiants</h2>
        <p>Bonjour,</p>
        <p>Voici vos identifiants de connexion pour votre compte École Al Markaz :</p>
        <div style="background-color: #f0f0f0; padding: 15px; margin: 20px 0;">
            <p><strong>Identifiant:</strong> {username}</p>
            <p><strong>Mot de passe:</strong> {password}</p>
        </div>
        <p>Veuillez conserver ces informations en lieu sûr.</p>
        <p>Cordialement,<br>L'équipe de gestion de l'École Al Markaz</p>
    </body>
    </html>
    """
    
    try:
        email_message = EmailMultiAlternatives(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [to_email]
        )
        email_message.attach_alternative(html_message, "text/html")
        email_message.send()
        
        print(f"✅ Email envoyé avec succès à {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi à {to_email}: {e}")
        
        # Sauvegarder dans un fichier de secours
        try:
            log_dir = os.path.join(settings.BASE_DIR, 'email_logs')
            os.makedirs(log_dir, exist_ok=True)
            with open(os.path.join(log_dir, 'credentials_backup.txt'), 'a', encoding='utf-8') as f:
                f.write(f"Destinataire: {to_email}\n")
                f.write(f"Identifiant: {username}\n")
                f.write(f"Mot de passe: {password}\n")
                f.write(f"Date: {import datetime; datetime.datetime.now()}\n")
                f.write("-" * 50 + "\n")
        except:
            pass
        
        return False
