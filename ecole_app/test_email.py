from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
import logging
import os

def test_email_config(request):
    """Vue de test pour diagnostiquer les problèmes d'email"""
    
    if request.method == 'POST':
        test_email = request.POST.get('email', 'mymarkaz02@gmail.com')
        
        try:
            # Test d'envoi simple
            send_mail(
                'Test Email - École Al Markaz',
                'Ceci est un email de test pour vérifier la configuration.',
                settings.DEFAULT_FROM_EMAIL,
                [test_email],
                fail_silently=False,
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Email envoyé avec succès à {test_email}'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'config': {
                    'email_backend': settings.EMAIL_BACKEND,
                    'email_host': settings.EMAIL_HOST,
                    'email_port': settings.EMAIL_PORT,
                    'email_use_tls': settings.EMAIL_USE_TLS,
                    'default_from_email': settings.DEFAULT_FROM_EMAIL,
                    'email_host_user': settings.EMAIL_HOST_USER,
                }
            })
    
    return render(request, 'ecole_app/test_email.html')
