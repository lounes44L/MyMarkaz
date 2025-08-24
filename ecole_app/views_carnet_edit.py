from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import EcouteAvantMemo, Memorisation, Revision, Repetition
from .forms import EcouteAvantMemoForm, MemorisationForm, RevisionForm, RepetitionForm
from .views_carnet import check_eleve_access

@login_required
def modifier_ecoute(request, ecoute_id):
    """Modifier une séance d'écoute"""
    ecoute = get_object_or_404(EcouteAvantMemo, id=ecoute_id)
    carnet = ecoute.carnet
    eleve = carnet.eleve
    
    # Vérifier les permissions d'accès
    eleve_check, has_access = check_eleve_access(request, eleve.id)
    if not has_access:
        messages.error(request, "Vous n'avez pas accès au carnet de cet élève.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EcouteAvantMemoForm(request.POST, instance=ecoute)
        if form.is_valid():
            form.save()
            messages.success(request, "Séance d'écoute modifiée avec succès.")
            return redirect('carnet_pedagogique', eleve_id=eleve.id)
    else:
        form = EcouteAvantMemoForm(instance=ecoute)
    
    context = {
        'form': form,
        'eleve': eleve,
        'titre_page': "Modifier une séance d'écoute",
        'is_update': True
    }
    return render(request, 'ecole_app/carnet/formulaire.html', context)

@login_required
def supprimer_ecoute(request, ecoute_id):
    """Supprimer une séance d'écoute"""
    ecoute = get_object_or_404(EcouteAvantMemo, id=ecoute_id)
    carnet = ecoute.carnet
    eleve = carnet.eleve
    
    # Vérifier les permissions d'accès
    eleve_check, has_access = check_eleve_access(request, eleve.id)
    if not has_access:
        messages.error(request, "Vous n'avez pas accès au carnet de cet élève.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        ecoute.delete()
        messages.success(request, "Séance d'écoute supprimée avec succès.")
        return redirect('carnet_pedagogique', eleve_id=eleve.id)
    
    context = {
        'eleve': eleve,
        'titre_page': "Supprimer une séance d'écoute",
        'objet': ecoute,
        'type_objet': "séance d'écoute",
        'date_objet': ecoute.date
    }
    return render(request, 'ecole_app/carnet/confirmer_suppression.html', context)

@login_required
def modifier_memorisation(request, memorisation_id):
    """Modifier une séance de mémorisation"""
    memorisation = get_object_or_404(Memorisation, id=memorisation_id)
    carnet = memorisation.carnet
    eleve = carnet.eleve
    
    # Vérifier les permissions d'accès
    eleve_check, has_access = check_eleve_access(request, eleve.id)
    if not has_access:
        messages.error(request, "Vous n'avez pas accès au carnet de cet élève.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = MemorisationForm(request.POST, instance=memorisation)
        if form.is_valid():
            form.save()
            messages.success(request, "Séance de mémorisation modifiée avec succès.")
            return redirect('carnet_pedagogique', eleve_id=eleve.id)
    else:
        form = MemorisationForm(instance=memorisation)
    
    context = {
        'form': form,
        'eleve': eleve,
        'titre_page': "Modifier une séance de mémorisation",
        'is_update': True
    }
    return render(request, 'ecole_app/carnet/formulaire.html', context)

@login_required
def supprimer_memorisation(request, memorisation_id):
    """Supprimer une séance de mémorisation"""
    memorisation = get_object_or_404(Memorisation, id=memorisation_id)
    carnet = memorisation.carnet
    eleve = carnet.eleve
    
    # Vérifier les permissions d'accès
    eleve_check, has_access = check_eleve_access(request, eleve.id)
    if not has_access:
        messages.error(request, "Vous n'avez pas accès au carnet de cet élève.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        memorisation.delete()
        messages.success(request, "Séance de mémorisation supprimée avec succès.")
        return redirect('carnet_pedagogique', eleve_id=eleve.id)
    
    context = {
        'eleve': eleve,
        'titre_page': "Supprimer une séance de mémorisation",
        'objet': memorisation,
        'type_objet': "séance de mémorisation",
        'date_objet': memorisation.date
    }
    return render(request, 'ecole_app/carnet/confirmer_suppression.html', context)

@login_required
def modifier_revision(request, revision_id):
    """Modifier une révision"""
    revision = get_object_or_404(Revision, id=revision_id)
    carnet = revision.carnet
    eleve = carnet.eleve
    
    # Vérifier les permissions d'accès
    eleve_check, has_access = check_eleve_access(request, eleve.id)
    if not has_access:
        messages.error(request, "Vous n'avez pas accès au carnet de cet élève.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RevisionForm(request.POST, instance=revision)
        if form.is_valid():
            form.save()
            messages.success(request, "Révision modifiée avec succès.")
            return redirect('carnet_pedagogique', eleve_id=eleve.id)
    else:
        form = RevisionForm(instance=revision)
    
    context = {
        'form': form,
        'eleve': eleve,
        'titre_page': "Modifier une révision",
        'is_update': True
    }
    return render(request, 'ecole_app/carnet/formulaire.html', context)

@login_required
def supprimer_revision(request, revision_id):
    """Supprimer une révision"""
    revision = get_object_or_404(Revision, id=revision_id)
    carnet = revision.carnet
    eleve = carnet.eleve
    
    # Vérifier les permissions d'accès
    eleve_check, has_access = check_eleve_access(request, eleve.id)
    if not has_access:
        messages.error(request, "Vous n'avez pas accès au carnet de cet élève.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        revision.delete()
        messages.success(request, "Révision supprimée avec succès.")
        return redirect('carnet_pedagogique', eleve_id=eleve.id)
    
    context = {
        'eleve': eleve,
        'titre_page': "Supprimer une révision",
        'objet': revision,
        'type_objet': "révision hebdomadaire",
        'date_objet': revision.date
    }
    return render(request, 'ecole_app/carnet/confirmer_suppression.html', context)

@login_required
def modifier_repetition(request, repetition_id):
    """Modifier une répétition"""
    repetition = get_object_or_404(Repetition, id=repetition_id)
    carnet = repetition.carnet
    eleve = carnet.eleve
    
    # Vérifier les permissions d'accès
    eleve_check, has_access = check_eleve_access(request, eleve.id)
    if not has_access:
        messages.error(request, "Vous n'avez pas accès au carnet de cet élève.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RepetitionForm(request.POST, instance=repetition)
        if form.is_valid():
            form.save()
            messages.success(request, "Répétition modifiée avec succès.")
            return redirect('carnet_pedagogique', eleve_id=eleve.id)
    else:
        form = RepetitionForm(instance=repetition)
    
    context = {
        'form': form,
        'eleve': eleve,
        'titre_page': "Modifier une répétition",
        'is_update': True
    }
    return render(request, 'ecole_app/carnet/formulaire.html', context)

@login_required
def supprimer_repetition(request, repetition_id):
    """Supprimer une répétition"""
    repetition = get_object_or_404(Repetition, id=repetition_id)
    carnet = repetition.carnet
    eleve = carnet.eleve
    
    # Vérifier les permissions d'accès
    eleve_check, has_access = check_eleve_access(request, eleve.id)
    if not has_access:
        messages.error(request, "Vous n'avez pas accès au carnet de cet élève.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        repetition.delete()
        messages.success(request, "Répétition supprimée avec succès.")
        return redirect('carnet_pedagogique', eleve_id=eleve.id)
    
    context = {
        'eleve': eleve,
        'titre_page': "Supprimer une répétition",
        'objet': repetition,
        'type_objet': "répétition",
        'date_objet': repetition.derniere_date
    }
    return render(request, 'ecole_app/carnet/confirmer_suppression.html', context)
