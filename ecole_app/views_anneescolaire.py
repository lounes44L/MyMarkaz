from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import AnneeScolaire
from .forms import AnneeScolaireForm

@login_required
def liste_anneescolaire(request):
    """Affiche la liste des années scolaires"""
    anneescolaires = AnneeScolaire.objects.all().order_by('-nom')
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    
    context = {
        'anneescolaires': anneescolaires,
        'annee_active': annee_active,
        'titre': "Années scolaires",
    }
    return render(request, 'ecole_app/anneescolaire/liste.html', context)

@login_required
def ajouter_anneescolaire(request):
    """Ajoute une nouvelle année scolaire"""
    if request.method == 'POST':
        form = AnneeScolaireForm(request.POST)
        if form.is_valid():
            anneescolaire = form.save()
            messages.success(request, f"L'année scolaire {anneescolaire.nom} a été ajoutée avec succès !")
            return redirect('liste_anneescolaire')
    else:
        form = AnneeScolaireForm()
    
    context = {
        'form': form,
        'titre': "Ajouter une année scolaire",
        'submit_text': "Ajouter",
    }
    return render(request, 'ecole_app/anneescolaire/formulaire.html', context)

@login_required
def modifier_anneescolaire(request, annee_id):
    """Modifie une année scolaire existante"""
    anneescolaire = get_object_or_404(AnneeScolaire, id=annee_id)
    
    if request.method == 'POST':
        form = AnneeScolaireForm(request.POST, instance=anneescolaire)
        if form.is_valid():
            anneescolaire = form.save()
            messages.success(request, f"L'année scolaire {anneescolaire.nom} a été modifiée avec succès !")
            return redirect('liste_anneescolaire')
    else:
        form = AnneeScolaireForm(instance=anneescolaire)
    
    context = {
        'form': form,
        'titre': f"Modifier l'année scolaire {anneescolaire.nom}",
        'submit_text': "Modifier",
    }
    return render(request, 'ecole_app/anneescolaire/formulaire.html', context)

@login_required
@require_POST
def supprimer_anneescolaire(request, annee_id):
    """Supprime une année scolaire"""
    anneescolaire = get_object_or_404(AnneeScolaire, id=annee_id)
    nom = anneescolaire.nom
    anneescolaire.delete()
    messages.success(request, f"L'année scolaire {nom} a été supprimée avec succès !")
    return redirect('liste_anneescolaire')

@login_required
@require_POST
def activer_anneescolaire(request, annee_id):
    """Active une année scolaire et désactive les autres"""
    anneescolaire = get_object_or_404(AnneeScolaire, id=annee_id)
    # Désactiver toutes les années scolaires
    AnneeScolaire.objects.all().update(active=False)
    # Activer l'année sélectionnée
    anneescolaire.active = True
    anneescolaire.save()
    messages.success(request, f"L'année scolaire {anneescolaire.nom} est maintenant l'année active.")
    return redirect('liste_anneescolaire')
