from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import ObjectifMensuel, Eleve
from .decorators import eleve_required
from .views_objectifs import calculer_progression

@login_required
@eleve_required
def gestion_objectifs(request):
    """
    Vue pour afficher et gérer les objectifs mensuels de l'élève
    """
    eleve = request.user.eleve
    
    # Récupérer l'objectif du mois actuel
    mois_actuel = timezone.now().replace(day=1)
    objectif_actuel = ObjectifMensuel.objects.filter(
        eleve=eleve,
        mois__year=mois_actuel.year,
        mois__month=mois_actuel.month
    ).first()
    
    # Récupérer l'historique des objectifs
    objectifs = ObjectifMensuel.objects.filter(eleve=eleve).order_by('-mois')
    
    # Calculer le pourcentage de progression
    progression_pourcentage = calculer_progression(eleve)
    
    context = {
        'eleve': eleve,
        'objectif_actuel': objectif_actuel,
        'objectifs': objectifs,
        'progression_pourcentage': progression_pourcentage,
    }
    
    return render(request, 'ecole_app/eleves/gestion_objectifs.html', context)
