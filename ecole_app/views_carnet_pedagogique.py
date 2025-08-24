from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Eleve, CompetenceLivre, EvaluationCompetence
from django.db.models import Prefetch

@login_required
def carnet_pedagogique(request, eleve_id):
    """
    Affiche le carnet pédagogique d'un élève avec les compétences à évaluer
    """
    eleve = get_object_or_404(Eleve, pk=eleve_id)
    
    # Récupérer les compétences pour les leçons 1 et 2
    competences = CompetenceLivre.objects.filter(lecon__in=[1, 2]).order_by('lecon', 'ordre')
    
    # Récupérer les évaluations existantes pour cet élève
    evaluations = EvaluationCompetence.objects.filter(
        eleve=eleve,
        competence__in=competences
    ).select_related('competence')
    
    # Créer un dictionnaire pour faciliter l'accès aux évaluations
    evaluations_dict = {eval.competence_id: eval for eval in evaluations}
    
    # Préparer les données pour le template
    competences_par_lecon = {}
    for comp in competences:
        if comp.lecon not in competences_par_lecon:
            competences_par_lecon[comp.lecon] = []
        
        # Ajouter l'évaluation si elle existe, sinon None
        evaluation = evaluations_dict.get(comp.id)
        competences_par_lecon[comp.lecon].append({
            'competence': comp,
            'evaluation': evaluation
        })
    
    context = {
        'eleve': eleve,
        'competences_par_lecon': competences_par_lecon,
    }
    
    return render(request, 'ecole_app/eleves/carnet_pedagogique.html', context)

@login_required
@require_POST
def evaluer_competence(request):
    """
    Met à jour l'évaluation d'une compétence pour un élève
    """
    eleve_id = request.POST.get('eleve_id')
    competence_id = request.POST.get('competence_id')
    statut = request.POST.get('statut')
    
    if not eleve_id or not competence_id or not statut:
        return JsonResponse({'success': False, 'error': 'Paramètres manquants'}, status=400)
    
    if statut not in [choice[0] for choice in EvaluationCompetence.STATUT_CHOICES]:
        return JsonResponse({'success': False, 'error': 'Statut invalide'}, status=400)
    
    eleve = get_object_or_404(Eleve, pk=eleve_id)
    competence = get_object_or_404(CompetenceLivre, pk=competence_id)
    
    # Créer ou mettre à jour l'évaluation
    evaluation, created = EvaluationCompetence.objects.update_or_create(
        eleve=eleve,
        competence=competence,
        defaults={'statut': statut}
    )
    
    return JsonResponse({
        'success': True, 
        'created': created,
        'statut': evaluation.statut,
        'statut_display': evaluation.get_statut_display()
    })
