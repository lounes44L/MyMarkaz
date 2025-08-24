from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime
from .models import ObjectifMensuel, Eleve
from .decorators import eleve_required

@login_required
@eleve_required
def ajouter_objectif(request):
    """
    Vue pour ajouter un nouvel objectif mensuel pour l'élève connecté
    """
    if request.method == 'POST':
        eleve_id = request.POST.get('eleve_id')
        type_objectif = request.POST.get('type_objectif')
        
        # Vérifier si l'élève existe
        eleve = get_object_or_404(Eleve, id=eleve_id)
        
        # Vérifier que l'élève connecté est bien celui qui ajoute l'objectif
        if request.user.eleve.id != eleve.id:
            messages.error(request, "Vous n'êtes pas autorisé à ajouter un objectif pour cet élève.")
            return redirect('dashboard_eleve')
        
        # Récupérer le mois et l'année actuels
        mois_actuel = timezone.now().replace(day=1)
        
        # Vérifier si un objectif existe déjà pour ce mois
        objectif_existant = ObjectifMensuel.objects.filter(
            eleve=eleve,
            mois__year=mois_actuel.year,
            mois__month=mois_actuel.month
        ).first()
        
        # Si un objectif existe déjà, le mettre à jour
        if objectif_existant:
            objectif = objectif_existant
            message_type = "info"
            message_text = "Votre objectif du mois a été mis à jour."
        else:
            # Sinon, créer un nouvel objectif
            objectif = ObjectifMensuel(
                eleve=eleve,
                mois=mois_actuel,
                statut='en_cours'
            )
            message_type = "success"
            message_text = "Votre objectif du mois a été créé avec succès."
        
        # Mettre à jour les champs selon le type d'objectif
        if type_objectif == 'sourate':
            objectif.sourate = request.POST.get('sourate')
            page_objectif = request.POST.get('page_objectif')
            objectif.page_debut = page_objectif  # Utiliser la même valeur pour page_debut
            objectif.page_fin = page_objectif    # Utiliser la même valeur pour page_fin
            objectif.numero_exercice = None
            objectif.description_libre = None
        elif type_objectif == 'exercice':
            objectif.sourate = None
            objectif.page_debut = None
            objectif.page_fin = None
            objectif.numero_exercice = request.POST.get('numero_exercice')
            objectif.description_libre = None
        elif type_objectif == 'libre':
            objectif.sourate = None
            objectif.page_debut = None
            objectif.page_fin = None
            objectif.numero_exercice = None
            objectif.description_libre = request.POST.get('description_libre')
        
        objectif.save()
        
        return redirect('dashboard_eleve')
    
    # Si la méthode n'est pas POST, rediriger vers le dashboard
    return redirect('dashboard_eleve')

@login_required
@eleve_required
def modifier_statut_objectif(request, objectif_id, statut):
    """
    Vue pour modifier le statut d'un objectif (atteint ou non atteint)
    """
    # Vérifier si l'objectif existe
    objectif = get_object_or_404(ObjectifMensuel, id=objectif_id)
    
    # Vérifier que l'élève connecté est bien le propriétaire de l'objectif
    if request.user.eleve.id != objectif.eleve.id:
        messages.error(request, "Vous n'êtes pas autorisé à modifier cet objectif.")
        return redirect('dashboard_eleve')
    
    # Mettre à jour le statut
    if statut in ['atteint', 'non_atteint', 'en_cours']:
        objectif.statut = statut
        objectif.save()
        
        if statut == 'atteint':
            messages.success(request, "Félicitations ! Votre objectif a été marqué comme atteint.")
        elif statut == 'non_atteint':
            messages.warning(request, "Votre objectif a été marqué comme non atteint.")
        else:
            messages.info(request, "Votre objectif a été remis en cours.")
    else:
        messages.error(request, "Statut non valide.")
    
    return redirect('dashboard_eleve')

def calculer_progression(eleve):
    """
    Fonction utilitaire pour calculer le pourcentage de progression de mémorisation du Coran
    basé sur la page actuelle et la direction de mémorisation
    """
    from .models import ProgressionCoran
    
    # Essayer de récupérer la progression du Coran de l'élève
    try:
        progression = ProgressionCoran.objects.get(eleve=eleve)
        return progression.calculer_pourcentage()
    except ProgressionCoran.DoesNotExist:
        # Si aucune progression n'existe, créer une nouvelle entrée avec des valeurs par défaut
        progression = ProgressionCoran(eleve=eleve, page_actuelle=1, direction_memorisation='debut')
        progression.save()
        return 0


def ajouter_progression_coran(request):
    """
    Vue pour ajouter ou mettre à jour la progression de mémorisation du Coran
    """
    from .models import ProgressionCoran, Eleve
    from django.contrib import messages
    from django.shortcuts import redirect
    
    if request.method == 'POST':
        eleve_id = request.POST.get('eleve_id')
        sourate = request.POST.get('sourate')
        page = request.POST.get('page_objectif')
        page_debut_sourate = request.POST.get('page_debut_sourate')
        direction = request.POST.get('direction_memorisation')
        
        # Convertir la page en entier avec validation
        try:
            page = int(page) if page else 1
            if page < 1 or page > 604:
                messages.error(request, "La page doit être entre 1 et 604.")
                return redirect('dashboard_eleve')
        except (ValueError, TypeError):
            page = 1
            
        # Convertir la page de début de sourate en entier avec validation
        try:
            page_debut_sourate = int(page_debut_sourate) if page_debut_sourate else page
            if page_debut_sourate < 1 or page_debut_sourate > 604:
                page_debut_sourate = page
        except (ValueError, TypeError):
            page_debut_sourate = page
        
        try:
            eleve = Eleve.objects.get(id=eleve_id)
            
            # Vérifier que l'élève connecté est bien celui qui ajoute la progression
            if request.user.eleve.id != eleve.id:
                messages.error(request, "Vous n'êtes pas autorisé à modifier la progression pour cet élève.")
                return redirect('dashboard_eleve')
            
            # Récupérer ou créer la progression
            progression, created = ProgressionCoran.objects.get_or_create(
                eleve=eleve,
                defaults={
                    'sourate_actuelle': sourate,
                    'page_actuelle': page,
                    'page_debut_sourate': page_debut_sourate,
                    'direction_memorisation': direction
                }
            )
            
            # Si la progression existe déjà, mettre à jour les valeurs
            if not created:
                progression.sourate_actuelle = sourate
                progression.page_actuelle = page
                progression.page_debut_sourate = page_debut_sourate
                progression.direction_memorisation = direction
                progression.save()
            
            messages.success(request, "Votre progression a été mise à jour avec succès.")
        except Eleve.DoesNotExist:
            messages.error(request, "Élève non trouvé.")
        
        return redirect('dashboard_eleve')
    
    # Si la méthode n'est pas POST, rediriger vers le dashboard
    return redirect('dashboard_eleve')
