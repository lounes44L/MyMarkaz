from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import (Eleve, CarnetPedagogique, EcouteAvantMemo, 
                    Memorisation, Revision, Repetition, Classe)
from .views_carnet import check_eleve_access

@login_required
def eleves_par_classe(request, classe_id):
    """
    API pour récupérer la liste des élèves d'une classe spécifique
    """
    try:
        # Vérifier si la classe existe
        classe = Classe.objects.get(pk=classe_id)
        
        # Récupérer les élèves de cette classe qui ne sont pas archivés
        eleves = Eleve.objects.filter(
            classes=classe,
            archive=False
        ).order_by('nom', 'prenom')
        
        # Préparer les données pour le JSON
        eleves_data = [{
            'id': eleve.id,
            'nom': eleve.nom,
            'prenom': eleve.prenom
        } for eleve in eleves]
        
        return JsonResponse(eleves_data, safe=False)
    except Classe.DoesNotExist:
        return JsonResponse({'error': 'Classe non trouvée'}, status=404)

@login_required
def api_carnet_data(request, eleve_id=None):
    """API pour récupérer les données du carnet pédagogique filtrées par mois/année"""
    # Vérifier les permissions d'accès
    eleve, has_access = check_eleve_access(request, eleve_id)
    if not has_access:
        return JsonResponse({'error': "Vous n'avez pas accès au carnet de cet élève."}, status=403)
    
    # Récupérer le carnet pédagogique
    carnet, created = CarnetPedagogique.objects.get_or_create(eleve=eleve)
    
    # Récupérer le mois et l'année depuis les paramètres GET
    date_actuelle = timezone.now()
    try:
        mois = int(request.GET.get('mois', date_actuelle.month))
        annee = int(request.GET.get('annee', date_actuelle.year))
        
        # Vérifier que les valeurs sont dans des plages valides
        if mois < 1 or mois > 12:
            mois = date_actuelle.month
        if annee < 2000 or annee > 2100:  # Plage raisonnable pour les années
            annee = date_actuelle.year
    except (ValueError, TypeError):
        # En cas d'erreur de conversion, utiliser les valeurs par défaut
        mois = date_actuelle.month
        annee = date_actuelle.year
    
    # Filtrer les données par mois et année
    ecoutes = EcouteAvantMemo.objects.filter(
        carnet=carnet,
        date__month=mois,
        date__year=annee
    ).order_by('-date')
    
    memorisations = Memorisation.objects.filter(
        carnet=carnet,
        date__month=mois,
        date__year=annee
    ).order_by('-date')
    
    revisions = Revision.objects.filter(
        carnet=carnet,
        date__month=mois,
        date__year=annee
    ).order_by('-date')
    
    repetitions = Repetition.objects.filter(
        carnet=carnet,
        derniere_date__month=mois,
        derniere_date__year=annee
    ).order_by('-derniere_date')
    
    # Calculer les statistiques
    total_pages_memo = memorisations.aggregate(Sum('fin_page'))['fin_page__sum'] or 0
    
    # Préparer les données pour le JSON
    ecoutes_data = [{
        'id': e.id,
        'date': e.date.strftime('%d/%m/%Y'),
        'duree': e.duree,
        'sourate': e.sourate,
        'debut_verset': e.debut_verset,
        'fin_verset': e.fin_verset,
        'enseignant': e.enseignant.nom if e.enseignant else 'Non spécifié',
        'commentaire': e.commentaire
    } for e in ecoutes]
    
    memorisations_data = [{
        'id': m.id,
        'date': m.date.strftime('%d/%m/%Y'),
        'sourate': m.sourate,
        'debut_page': m.debut_page,
        'fin_page': m.fin_page,
        'enseignant': m.enseignant.nom if m.enseignant else 'Non spécifié',
        'commentaire': m.commentaire
    } for m in memorisations]
    
    revisions_data = [{
        'id': r.id,
        'date': r.date.strftime('%d/%m/%Y'),
        'semaine': r.semaine,
        'sourate': r.sourate,
        'debut_page': r.debut_page,
        'fin_page': r.fin_page,
        'enseignant': r.enseignant.nom if r.enseignant else 'Non spécifié',
        'commentaire': r.commentaire
    } for r in revisions]
    
    repetitions_data = [{
        'id': r.id,
        'derniere_date': r.derniere_date.strftime('%d/%m/%Y'),
        'sourate': r.sourate,
        'page': r.page,
        'nombre_repetitions': r.nombre_repetitions
    } for r in repetitions]
    
    # Renvoyer les données au format JSON
    return JsonResponse({
        'stats': {
            'memorisations_count': memorisations.count(),
            'total_pages_memo': total_pages_memo,
            'revisions_count': revisions.count(),
            'repetitions_count': repetitions.count()
        },
        'ecoutes': ecoutes_data,
        'memorisations': memorisations_data,
        'revisions': revisions_data,
        'repetitions': repetitions_data
    })

@login_required
@require_POST
def increment_repetition(request, repetition_id):
    """Incrémenter le nombre de répétitions d'une entrée"""
    repetition = get_object_or_404(Repetition, id=repetition_id)
    
    # Vérifier les permissions d'accès
    eleve = repetition.carnet.eleve
    eleve_check, has_access = check_eleve_access(request, eleve.id)
    if not has_access:
        return JsonResponse({'error': "Vous n'avez pas accès au carnet de cet élève."}, status=403)
    
    # Incrémenter le nombre de répétitions
    repetition.nombre_repetitions += 1
    # Ne pas mettre à jour la date
    repetition.save()
    
    return JsonResponse({
        'success': True,
        'repetition_id': repetition.id,
        'nombre_repetitions': repetition.nombre_repetitions,
        'derniere_date': repetition.derniere_date.strftime('%d/%m/%Y')
    })

@login_required
@require_POST
def decrement_repetition(request, repetition_id):
    """Décrémenter le nombre de répétitions d'une entrée"""
    repetition = get_object_or_404(Repetition, id=repetition_id)
    
    # Vérifier les permissions d'accès
    eleve = repetition.carnet.eleve
    eleve_check, has_access = check_eleve_access(request, eleve.id)
    if not has_access:
        return JsonResponse({'error': "Vous n'avez pas accès au carnet de cet élève."}, status=403)
    
    # Décrémenter le nombre de répétitions (minimum 0)
    if repetition.nombre_repetitions > 0:
        repetition.nombre_repetitions -= 1
        # Ne pas mettre à jour la date
        repetition.save()
    
    return JsonResponse({
        'success': True,
        'repetition_id': repetition.id,
        'nombre_repetitions': repetition.nombre_repetitions,
        'derniere_date': repetition.derniere_date.strftime('%d/%m/%Y')
    })
