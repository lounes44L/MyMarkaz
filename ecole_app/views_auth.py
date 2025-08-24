from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from .models import Eleve, Professeur, AnneeScolaire

def user_login(request):
    """Page de connexion pour tous les utilisateurs"""
    if request.user.is_authenticated:
        # Redirection en fonction du type d'utilisateur
        return redirect_based_on_role(request.user, request)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue, {user.get_full_name() or user.username} !')
            
            # Vérifier si c'est un professeur avec plusieurs composantes
            if hasattr(user, 'professeur') and user.professeur:
                if hasattr(user.professeur, 'composantes') and user.professeur.composantes.count() > 1:
                    # Vérifier si une composante est déjà sélectionnée
                    if not request.session.get('composante_id'):
                        messages.info(request, 'Veuillez sélectionner une composante.')
                        return redirect('selection_composante')
            
            # Redirection en fonction du rôle
            return redirect_based_on_role(user, request)
        else:
            messages.error(request, 'Identifiant ou mot de passe incorrect.')
    
    return render(request, 'ecole_app/auth/login.html')

def redirect_based_on_role(user, request=None):
    """Redirige l'utilisateur vers la page appropriée selon son rôle"""
    if user.is_superuser or user.is_staff:
        # Administrateurs et staff vers la sélection de composante
        return redirect('selection_composante')
    
    # Pour les professeurs
    if hasattr(user, 'professeur') and user.professeur:
        return redirect('dashboard_professeur')
    
    # Pour les élèves
    if hasattr(user, 'eleve') and user.eleve:
        return redirect('dashboard_eleve')
    
    # Par défaut
    return redirect('selection_composante')

def user_logout(request):
    """Déconnexion de l'utilisateur"""
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('login')

@login_required
def profile(request):
    """Page de profil de l'utilisateur connecté"""
    # Récupérer les informations sur l'utilisateur
    user = request.user
    
    # Déterminer le type d'utilisateur
    user_type = None
    profile_data = None
    
    if hasattr(user, 'professeur') and user.professeur:
        user_type = 'professeur'
        # Précharger les classes pour éviter les problèmes d'accès dans le template
        professeur = Professeur.objects.prefetch_related('classes').get(id=user.professeur.id)
        
        # Filtrer les classes par année scolaire active, comme dans dashboard_professeur
        annee_active = AnneeScolaire.objects.filter(active=True).first()
        if annee_active:
            # Créer une liste des classes filtrées pour l'année active
            classes_actives = professeur.classes.filter(annee_scolaire=annee_active)
            # Ajouter cette liste au contexte pour l'utiliser dans le template
            professeur.classes_actives = classes_actives
        
        profile_data = professeur
    elif hasattr(user, 'eleve') and user.eleve:
        user_type = 'eleve'
        profile_data = user.eleve
    
    context = {
        'user_type': user_type,
        'profile_data': profile_data,
    }
    
    # Utiliser un template différent selon le type d'utilisateur
    if user_type == 'eleve':
        return render(request, 'ecole_app/auth/profile_eleve.html', context)
    else:
        return render(request, 'ecole_app/auth/profile.html', context)

# Vérifications de rôle
def is_admin(user):
    """Vérifie si l'utilisateur est un administrateur"""
    return user.is_staff or user.is_superuser

def is_professeur(user):
    """Vérifie si l'utilisateur est un professeur"""
    return hasattr(user, 'professeur') and user.professeur is not None

def is_eleve(user):
    """Vérifie si l'utilisateur est un élève"""
    return hasattr(user, 'eleve') and user.eleve is not None

# Dashboards spécifiques
@login_required
@user_passes_test(is_professeur)
def dashboard_professeur(request):
    """Tableau de bord pour les professeurs"""
    from django.utils import timezone
    from .models import Composante
    
    professeur = request.user.professeur
    composante_selectionnee = None
    
    # Vérifier si le professeur enseigne dans plusieurs composantes
    if professeur.composantes.count() > 1:
        # Vérifier si une composante est sélectionnée dans la session
        composante_id = request.session.get('composante_id')
        if not composante_id:
            messages.info(request, 'Veuillez sélectionner une composante pour accéder à votre tableau de bord.')
            return redirect('selection_composante')
        
        # Vérifier que la composante sélectionnée appartient bien au professeur
        try:
            composante_selectionnee = professeur.composantes.get(id=composante_id)
        except Composante.DoesNotExist:
            # Si la composante n'existe pas ou n'appartient pas au professeur, effacer la session
            del request.session['composante_id']
            messages.warning(request, 'La composante sélectionnée n\'est pas valide. Veuillez en choisir une autre.')
            return redirect('selection_composante')
    elif professeur.composantes.count() == 1:
        # Si le professeur n'a qu'une seule composante, la sélectionner automatiquement
        composante_selectionnee = professeur.composantes.first()
        request.session['composante_id'] = composante_selectionnee.id
    
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    
    # Récupérer toutes les classes du professeur sans filtres pour diagnostic
    toutes_classes = professeur.classes.all()
    classes_count_total = toutes_classes.count()
    
    # Récupérer les classes du professeur pour affichage
    classes = professeur.classes.all()
    
    # Filtrer les classes par composante si une composante est sélectionnée
    if composante_selectionnee:
        classes = classes.filter(composante=composante_selectionnee)
        classes_count_composante = classes.count()
    else:
        classes_count_composante = classes.count()
    
    # Vérifier si une année scolaire active existe
    if annee_active:
        # Filtrer par année scolaire active
        classes = classes.filter(annee_scolaire=annee_active)
        classes_count_annee = classes.count()
    else:
        # Si aucune année scolaire active, ne pas filtrer par année
        classes_count_annee = classes.count()
        # Message d'avertissement si aucune année scolaire active
        messages.warning(request, "Attention: Aucune année scolaire active n'est définie. Toutes les classes sont affichées.")
    
    # Si aucune classe n'est trouvée après filtrage, afficher un message explicatif
    if classes.count() == 0 and classes_count_total > 0:
        if classes_count_composante == 0:
            messages.info(request, f"Vous avez {classes_count_total} classe(s) mais aucune n'est associée à la composante sélectionnée.")
        elif classes_count_annee == 0:
            messages.info(request, f"Vous avez {classes_count_composante} classe(s) dans cette composante, mais aucune n'est associée à l'année scolaire active.")
            
            # Option: afficher les classes sans filtrer par année scolaire si aucune n'est trouvée
            if classes_count_composante > 0:
                classes = professeur.classes.all()
                if composante_selectionnee:
                    classes = classes.filter(composante=composante_selectionnee)
    
    # Ajouter la date du jour pour le lien d'appel
    today = timezone.now().date()
    
    context = {
        'professeur': professeur,
        'classes': classes,
        'annee_active': annee_active,
        'today': today,
        'composante_selectionnee': composante_selectionnee,
    }
    return render(request, 'ecole_app/auth/dashboard_professeur.html', context)

from django.db.models import Sum

@login_required
@user_passes_test(is_eleve)
def dashboard_eleve(request):
    """Tableau de bord pour les élèves"""
    from .models import ObjectifMensuel, ProgressionCoran
    from datetime import datetime
    from django.utils import timezone
    from .views_objectifs import calculer_progression
    from django.contrib.messages import get_messages
    
    # Effacer les messages existants ou filtrer les messages non pertinents pour les élèves
    storage = get_messages(request)
    filtered_messages = []
    
    # Conserver uniquement les messages pertinents pour les élèves
    for message in storage:
        # Filtrer les messages concernant la sélection de composante
        if 'composante' not in message.message.lower() and 'sélectionner une composante' not in message.message.lower():
            filtered_messages.append(message)
    
    # Réinitialiser les messages filtrés dans la session
    storage.used = True
    
    # Réajouter les messages pertinents
    for message in filtered_messages:
        messages.add_message(request, message.level, message.message)
    
    eleve = request.user.eleve
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    
    # Récupérer les classes et les paiements de l'élève pour l'année active
    paiements = eleve.paiements.all()
    if annee_active:
        paiements = paiements.filter(annee_scolaire=annee_active)
    
    # Calcul du montant restant
    montant_total = getattr(eleve, 'montant_total', 0) or 0
    total_paye = paiements.aggregate(sum_montant=Sum('montant'))['sum_montant'] or 0
    montant_restant = max(montant_total - total_paye, 0)
    
    # Récupérer les objectifs mensuels de l'élève
    mois_actuel = timezone.now().replace(day=1)
    objectif_actuel = ObjectifMensuel.objects.filter(
        eleve=eleve,
        mois__year=mois_actuel.year,
        mois__month=mois_actuel.month
    ).first()
    
    # Récupérer l'historique des objectifs
    objectifs = ObjectifMensuel.objects.filter(eleve=eleve).order_by('-mois')
    
    # Calculer la progression du Coran
    progression_pourcentage = calculer_progression(eleve)
    
    # Récupérer la progression du Coran de l'élève
    try:
        progression_coran = ProgressionCoran.objects.get(eleve=eleve)
    except ProgressionCoran.DoesNotExist:
        progression_coran = None
    
    context = {
        'eleve': eleve,
        'paiements': paiements,
        'annee_active': annee_active,
        'montant_restant': montant_restant,
        'objectif_actuel': objectif_actuel,
        'objectifs': objectifs,
        'progression_pourcentage': progression_pourcentage,
        'progression_coran': progression_coran,
    }
    return render(request, 'ecole_app/auth/dashboard_eleve.html', context)

@login_required
def reset_password(request):
    """Permet à l'utilisateur de réinitialiser son mot de passe"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        user = request.user
        
        # Vérification du mot de passe actuel
        if not user.check_password(current_password):
            messages.error(request, 'Le mot de passe actuel est incorrect.')
            return redirect('reset_password')
        
        # Vérification de la correspondance des nouveaux mots de passe
        if new_password != confirm_password:
            messages.error(request, 'Les nouveaux mots de passe ne correspondent pas.')
            return redirect('reset_password')
        
        # Mise à jour du mot de passe
        user.set_password(new_password)
        user.save()
        
        # Reconnexion de l'utilisateur
        login(request, user)
        
        messages.success(request, 'Votre mot de passe a été modifié avec succès.')
        return redirect_based_on_role(user)
    
    # Déterminer le type d'utilisateur pour choisir le bon template
    user = request.user
    if hasattr(user, 'eleve') and user.eleve:
        return render(request, 'ecole_app/auth/reset_password_eleve.html')
    else:
        return render(request, 'ecole_app/auth/reset_password.html')

@login_required
@user_passes_test(is_admin)
def afficher_identifiants(request, type_utilisateur, id):
    """Affiche les identifiants générés pour un utilisateur nouvellement créé"""
    user = None
    nom = ""
    
    if type_utilisateur == 'eleve':
        eleve = Eleve.objects.filter(id=id, user__isnull=False).first()
        if eleve:
            user = eleve.user
            nom = f"{eleve.prenom} {eleve.nom}".strip()
    elif type_utilisateur == 'professeur':
        professeur = Professeur.objects.filter(id=id, user__isnull=False).first()
        if professeur:
            user = professeur.user
            nom = professeur.nom
    
    if not user:
        messages.error(request, "Utilisateur non trouvé ou aucun compte créé.")
        return redirect('dashboard')
    
    # Récupérer le mot de passe temporaire stocké (s'il existe encore)
    temp_password = getattr(eleve if type_utilisateur == 'eleve' else professeur, 'temp_password', None)
    
    context = {
        'user': user,
        'temp_password': temp_password,
        'nom': nom,
        'type_utilisateur': 'Élève' if type_utilisateur == 'eleve' else 'Professeur',
    }
    return render(request, 'ecole_app/auth/afficher_identifiants.html', context)
