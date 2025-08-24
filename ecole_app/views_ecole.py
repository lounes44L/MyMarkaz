from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import login
from django.db import transaction
from .models_ecole import Ecole
import random
import string

def inscription_ecole(request):
    """
    Vue pour l'inscription d'une nouvelle école et la création d'un compte administrateur
    """
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom_ecole = request.POST.get('nom_ecole')
        adresse = request.POST.get('adresse')
        telephone = request.POST.get('telephone')
        email = request.POST.get('email')
        site_web = request.POST.get('site_web')
        
        # Données de l'administrateur
        nom_admin = request.POST.get('nom_admin')
        email_admin = request.POST.get('email_admin')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validation des données
        if not nom_ecole or not nom_admin or not email_admin or not password:
            messages.error(request, "Tous les champs obligatoires doivent être remplis.")
            return render(request, 'ecole_app/ecole/inscription.html')
        
        if password != password_confirm:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, 'ecole_app/ecole/inscription.html')
        
        # Vérification que l'email n'est pas déjà utilisé
        if User.objects.filter(email=email_admin).exists():
            messages.error(request, "Cet email est déjà utilisé par un autre compte.")
            return render(request, 'ecole_app/ecole/inscription.html')
        
        try:
            with transaction.atomic():
                # Création du compte utilisateur administrateur
                username = email_admin.split('@')[0] + '_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
                user = User.objects.create_user(
                    username=username,
                    email=email_admin,
                    password=password,
                    first_name=nom_admin,
                    is_staff=True  # L'administrateur d'école a accès à l'interface d'administration
                )
                
                # Création de l'école
                ecole = Ecole.objects.create(
                    nom=nom_ecole,
                    adresse=adresse,
                    telephone=telephone,
                    email=email,
                    site_web=site_web,
                    admin=user
                )
                
                # Création d'un groupe pour les administrateurs d'école s'il n'existe pas
                admin_ecole_group, created = Group.objects.get_or_create(name='Administrateurs École')
                user.groups.add(admin_ecole_group)
                
                # Connexion automatique de l'utilisateur
                login(request, user)
                
                messages.success(request, f"Félicitations ! Votre école '{nom_ecole}' a été créée avec succès. Vous êtes maintenant connecté en tant qu'administrateur.")
                return redirect('dashboard')
                
        except Exception as e:
            messages.error(request, f"Une erreur est survenue lors de la création de votre compte : {str(e)}")
    
    return render(request, 'ecole_app/ecole/inscription.html')

def liste_ecoles(request):
    """
    Vue pour afficher la liste des écoles (accessible uniquement aux super-administrateurs)
    """
    if not request.user.is_superuser:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return redirect('dashboard')
    
    ecoles = Ecole.objects.all().order_by('nom')
    
    context = {
        'ecoles': ecoles
    }
    
    return render(request, 'ecole_app/ecole/liste_ecoles.html', context)

def detail_ecole(request, ecole_id):
    """
    Vue pour afficher les détails d'une école (accessible uniquement aux super-administrateurs)
    """
    if not request.user.is_superuser:
        messages.error(request, "Vous n'avez pas les permissions nécessaires pour accéder à cette page.")
        return redirect('dashboard')
    
    try:
        ecole = Ecole.objects.get(id=ecole_id)
    except Ecole.DoesNotExist:
        messages.error(request, "Cette école n'existe pas.")
        return redirect('liste_ecoles')
    
    context = {
        'ecole': ecole
    }
    
    return render(request, 'ecole_app/ecole/detail_ecole.html', context)
