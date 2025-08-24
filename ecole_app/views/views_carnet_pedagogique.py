from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from ..models import Eleve, Memorisation, EcouteAvantMemo, Repetition, Revision
from datetime import datetime

@login_required
def carnet_pedagogique(request, eleve_id):
    eleve = get_object_or_404(Eleve, id=eleve_id)
    # Récupérer le mois sélectionné (par défaut: mois courant)
    mois_str = request.GET.get('mois')
    annee_str = request.GET.get('annee')
    now = datetime.now()
    try:
        mois = int(mois_str) if mois_str else now.month
    except (ValueError, TypeError):
        mois = now.month
    annee = now.year
    try:
        annee = int(annee_str) if annee_str else now.year
    except (ValueError, TypeError):
        annee = now.year

    # Filtrer les éléments par mois/année
    memorisations = Memorisation.objects.filter(eleve=eleve, date__month=mois, date__year=annee)
    ecoutes = EcouteAvantMemo.objects.filter(eleve=eleve, date__month=mois, date__year=annee)
    repetitions = Repetition.objects.filter(carnet__eleve=eleve, date__month=mois, date__year=annee)
    revisions = Revision.objects.filter(carnet__eleve=eleve, date__month=mois, date__year=annee)

    # Statistiques
    total_pages_memo = memorisations.aggregate(total=Sum('pages'))['total'] or 0

    context = {
        'eleve': eleve,
        'memorisations': memorisations,
        'ecoutes': ecoutes,
        'repetitions': repetitions,
        'revisions': revisions,
        'total_pages_memo': total_pages_memo,
        'mois': mois,
        'annee': annee,
    }
    return render(request, 'ecole_app/carnet/index.html', context)
