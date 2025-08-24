from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Composante, AnneeScolaire, Eleve, Professeur, Classe
from .views_auth import is_admin

@login_required
def selection_composante(request):
    """Page de sélection de composante après connexion admin ou pour professeurs multi-composantes"""
    user = request.user
    
    # Déterminer les composantes à afficher selon le rôle de l'utilisateur
    if user.is_superuser or user.is_staff:
        # Pour les admins, afficher toutes les composantes actives
        composantes = Composante.objects.filter(active=True).order_by('nom')
    elif hasattr(user, 'professeur') and user.professeur:
        # Pour les professeurs, afficher uniquement leurs composantes
        composantes = user.professeur.composantes.filter(active=True).order_by('nom')
        
        # Si le professeur n'a qu'une seule composante, la sélectionner automatiquement
        if composantes.count() == 1:
            composante = composantes.first()
            request.session['composante_id'] = composante.id
            request.session['composante_nom'] = composante.nom
            messages.success(request, f'Composante "{composante.nom}" sélectionnée automatiquement.')
            return redirect('dashboard_professeur')
    else:
        # Rediriger les autres utilisateurs
        messages.error(request, 'Vous n\'avez pas accès à cette page.')
        return redirect('login')
    
    if request.method == 'POST':
        composante_id = request.POST.get('composante_id')
        if composante_id:
            try:
                # Vérifier que l'utilisateur a accès à cette composante
                if user.is_superuser or user.is_staff:
                    composante = Composante.objects.get(id=composante_id, active=True)
                else:
                    composante = user.professeur.composantes.get(id=composante_id, active=True)
                
                # Stocker la composante sélectionnée en session
                request.session['composante_id'] = composante.id
                request.session['composante_nom'] = composante.nom
                messages.success(request, f'Composante "{composante.nom}" sélectionnée.')
                
                # Rediriger selon le rôle
                if user.is_superuser or user.is_staff:
                    return redirect('dashboard')
                else:
                    return redirect('dashboard_professeur')
            except Composante.DoesNotExist:
                messages.error(request, 'Composante non trouvée ou non autorisée.')
    
    context = {
        'composantes': composantes,
    }
    return render(request, 'ecole_app/composante/selection.html', context)

@login_required
@user_passes_test(is_admin)
def gestion_composantes(request):
    """Page de gestion des composantes (CRUD)"""
    composantes = Composante.objects.all().order_by('nom')
    
    context = {
        'composantes': composantes,
    }
    return render(request, 'ecole_app/composante/gestion.html', context)

@login_required
@user_passes_test(is_admin)
def creer_composante(request):
    """Créer une nouvelle composante"""
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not nom:
            messages.error(request, 'Le nom de la composante est obligatoire.')
            return redirect('gestion_composantes')
        
        # Vérifier l'unicité du nom
        if Composante.objects.filter(nom=nom).exists():
            messages.error(request, f'Une composante avec le nom "{nom}" existe déjà.')
            return redirect('gestion_composantes')
        
        # Créer la composante
        composante = Composante.objects.create(
            nom=nom,
            description=description,
            active=True
        )
        
        # Créer automatiquement une première année scolaire pour cette composante
        annee_courante = f"{2024}-{2025}"  # Vous pouvez ajuster selon vos besoins
        AnneeScolaire.objects.create(
            composante=composante,
            nom=annee_courante,
            date_debut="2024-09-01",
            date_fin="2025-06-30",
            active=True
        )
        
        messages.success(request, f'Composante "{nom}" créée avec succès avec une année scolaire par défaut.')
        return redirect('gestion_composantes')
    
    return redirect('gestion_composantes')

@login_required
@user_passes_test(is_admin)
def modifier_composante(request, composante_id):
    """Modifier une composante existante"""
    composante = get_object_or_404(Composante, id=composante_id)
    
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        description = request.POST.get('description', '').strip()
        active = request.POST.get('active') == 'on'
        
        if not nom:
            messages.error(request, 'Le nom de la composante est obligatoire.')
            return redirect('gestion_composantes')
        
        # Vérifier l'unicité du nom (sauf pour la composante actuelle)
        if Composante.objects.filter(nom=nom).exclude(id=composante.id).exists():
            messages.error(request, f'Une composante avec le nom "{nom}" existe déjà.')
            return redirect('gestion_composantes')
        
        # Mettre à jour la composante
        composante.nom = nom
        composante.description = description
        composante.active = active
        composante.save()
        
        messages.success(request, f'Composante "{nom}" modifiée avec succès.')
        return redirect('gestion_composantes')
    
    context = {
        'composante': composante,
    }
    return render(request, 'ecole_app/composante/modifier.html', context)

@login_required
@user_passes_test(is_admin)
@require_POST
def supprimer_composante(request, composante_id):
    """Supprimer une composante (avec confirmation)"""
    composante = get_object_or_404(Composante, id=composante_id)
    
    # Vérifier s'il y a des données liées
    nb_eleves = composante.eleves.count()
    nb_professeurs = composante.professeurs.count()
    nb_classes = composante.classes.count()
    
    if nb_eleves > 0 or nb_professeurs > 0 or nb_classes > 0:
        messages.error(request, 
            f'Impossible de supprimer "{composante.nom}". '
            f'Cette composante contient {nb_eleves} élève(s), '
            f'{nb_professeurs} professeur(s) et {nb_classes} classe(s).')
        return redirect('gestion_composantes')
    
    nom_composante = composante.nom
    composante.delete()
    
    messages.success(request, f'Composante "{nom_composante}" supprimée avec succès.')
    return redirect('gestion_composantes')

@login_required
@user_passes_test(is_admin)
def changer_composante(request):
    """Changer de composante en cours de session"""
    if request.method == 'POST':
        composante_id = request.POST.get('composante_id')
        if composante_id:
            try:
                composante = Composante.objects.get(id=composante_id, active=True)
                request.session['composante_id'] = composante.id
                request.session['composante_nom'] = composante.nom
                messages.success(request, f'Basculé vers la composante "{composante.nom}".')
                return redirect('dashboard')
            except Composante.DoesNotExist:
                messages.error(request, 'Composante non trouvée.')
    
    return redirect('selection_composante')

def get_composante_courante(request):
    """Fonction utilitaire pour récupérer la composante courante depuis la session"""
    composante_id = request.session.get('composante_id')
    if composante_id:
        try:
            return Composante.objects.get(id=composante_id, active=True)
        except Composante.DoesNotExist:
            pass
    return None

@login_required
@user_passes_test(is_admin)
def statistiques_composante(request, composante_id):
    """Afficher les statistiques d'une composante"""
    composante = get_object_or_404(Composante, id=composante_id)
    
    # Statistiques générales
    nb_eleves = composante.eleves.count()
    nb_professeurs = composante.professeurs.count()
    nb_classes = composante.classes.count()
    nb_annees = composante.annees_scolaires.count()
    
    # Statistiques par année scolaire
    annees_stats = []
    for annee in composante.annees_scolaires.all():
        eleves_annee = composante.eleves.filter(annee_scolaire=annee).count()
        classes_annee = composante.classes.filter(annee_scolaire=annee).count()
        annees_stats.append({
            'annee': annee,
            'eleves': eleves_annee,
            'classes': classes_annee,
        })
    
    context = {
        'composante': composante,
        'nb_eleves': nb_eleves,
        'nb_professeurs': nb_professeurs,
        'nb_classes': nb_classes,
        'nb_annees': nb_annees,
        'annees_stats': annees_stats,
    }
    return render(request, 'ecole_app/composante/statistiques.html', context)
