from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from ..models import Eleve, Professeur, Memorisation, EcouteAvantMemo, Repetition, Revision
from ..forms import MemorisationForm, EcouteAvantMemoForm, RepetitionForm, RevisionForm

@login_required
def ajouter_memorisation(request, eleve_id):
    """Vue pour ajouter une mémorisation au carnet pédagogique d'un élève"""
    eleve = get_object_or_404(Eleve, id=eleve_id)
    
    if request.method == 'POST':
        form = MemorisationForm(request.POST)
        if form.is_valid():
            memorisation = form.save(commit=False)
            # Associer le carnet pédagogique de l'élève
            carnet = getattr(eleve, 'carnet_pedagogique', None)
            if carnet is None:
                carnet = CarnetPedagogique.objects.create(eleve=eleve)
            memorisation.carnet = carnet
            memorisation.date_creation = timezone.now()
            memorisation.save()
            messages.success(request, "Mémorisation ajoutée avec succès.")
            return redirect('carnet_pedagogique', eleve_id=eleve.id)
    else:
        form = MemorisationForm(initial={
            'date': timezone.now().date(),
            'enseignant': request.user if hasattr(request.user, 'enseignant') else None
        })
    
    return render(request, 'ecole_app/carnet/ajouter_memorisation.html', {
        'form': form,
        'eleve': eleve
    })

@login_required
def modifier_memorisation(request, memorisation_id):
    """Vue pour modifier une mémorisation existante"""
    memorisation = get_object_or_404(Memorisation, id=memorisation_id)
    # Accéder à l'élève via le carnet pédagogique
    carnet = memorisation.carnet
    eleve = carnet.eleve if carnet else None
    
    # Debugging
    print(f"DEBUG: Memorisation ID: {memorisation_id}")
    print(f"DEBUG: Carnet: {carnet}")
    print(f"DEBUG: Eleve: {eleve}")
    print(f"DEBUG: Eleve ID: {eleve.id if eleve else 'None'}")
    
    # Si l'élève est None, essayer de le récupérer directement
    if eleve is None and carnet:
        try:
            from ecole_app.models import Eleve
            eleve = Eleve.objects.filter(carnet_pedagogique=carnet).first()
            print(f"DEBUG: Eleve récupéré directement: {eleve}")
        except Exception as e:
            print(f"DEBUG: Erreur lors de la récupération directe de l'élève: {e}")
    
    if request.method == 'POST':
        form = MemorisationForm(request.POST, instance=memorisation)
        if form.is_valid():
            form.save()
            messages.success(request, "Mémorisation modifiée avec succès.")
            if eleve and eleve.id:
                return redirect('carnet_pedagogique', eleve_id=eleve.id)
            else:
                # Fallback si l'élève n'est pas disponible
                return redirect('liste_eleves')
    else:
        form = MemorisationForm(instance=memorisation)
    
    return render(request, 'ecole_app/carnet/modifier_memorisation.html', {
        'form': form,
        'memorisation': memorisation,
        'eleve': eleve  # Ajouter l'élève au contexte pour le template
    })

@login_required
def supprimer_memorisation(request, memorisation_id):
    """Vue pour supprimer une mémorisation"""
    memorisation = get_object_or_404(Memorisation, id=memorisation_id)
    # Accéder à l'élève via le carnet pédagogique
    eleve_id = memorisation.carnet.eleve.id
    
    memorisation.delete()
    messages.success(request, "Mémorisation supprimée avec succès.")
    return redirect('carnet_pedagogique', eleve_id=eleve_id)

@login_required
def ajouter_ecoute(request, eleve_id):
    """Vue pour ajouter une écoute au carnet pédagogique d'un élève"""
    eleve = get_object_or_404(Eleve, id=eleve_id)
    
    # Récupérer ou créer le carnet pédagogique de l'élève
    from ..models import CarnetPedagogique
    carnet, created = CarnetPedagogique.objects.get_or_create(eleve=eleve)
    
    if request.method == 'POST':
        form = EcouteAvantMemoForm(request.POST)
        if form.is_valid():
            ecoute = form.save(commit=False)
            ecoute.carnet = carnet  # Associer au carnet et non directement à l'élève
            ecoute.date_creation = timezone.now()
            ecoute.save()
            messages.success(request, "Écoute ajoutée avec succès.")
            return redirect('carnet_pedagogique', eleve_id=eleve.id)
    else:
        form = EcouteAvantMemoForm(initial={
            'date': timezone.now().date(),
            'enseignant': request.user if hasattr(request.user, 'enseignant') else None
        })
    
    return render(request, 'ecole_app/carnet/ajouter_ecoute.html', {
        'form': form,
        'eleve': eleve
    })

@login_required
def modifier_ecoute(request, ecoute_id):
    """Vue pour modifier une écoute existante"""
    ecoute = get_object_or_404(EcouteAvantMemo, id=ecoute_id)
    eleve = ecoute.carnet.eleve  # Accéder à l'élève via le carnet
    
    if request.method == 'POST':
        form = EcouteAvantMemoForm(request.POST, instance=ecoute)
        if form.is_valid():
            form.save()
            messages.success(request, "Écoute modifiée avec succès.")
            return redirect('carnet_pedagogique', eleve_id=eleve.id)
    else:
        form = EcouteAvantMemoForm(instance=ecoute)
    
    return render(request, 'ecole_app/carnet/modifier_ecoute.html', {
        'form': form,
        'ecoute': ecoute,
        'eleve': eleve,  # Ajouter l'élève au contexte pour le template
        'eleve_id': eleve.id  # Ajouter explicitement l'ID de l'élève
    })

@login_required
def supprimer_ecoute(request, ecoute_id):
    """Vue pour supprimer une écoute"""
    ecoute = get_object_or_404(EcouteAvantMemo, id=ecoute_id)
    eleve_id = ecoute.carnet.eleve.id  # Accéder à l'élève via le carnet
    
    ecoute.delete()
    messages.success(request, "Écoute supprimée avec succès.")
    return redirect('carnet_pedagogique', eleve_id=eleve_id)

@login_required
def ajouter_repetition(request, eleve_id):
    """Vue pour ajouter une répétition au carnet pédagogique d'un élève"""
    eleve = get_object_or_404(Eleve, id=eleve_id)
    
    # Récupérer ou créer le carnet pédagogique de l'élève
    from ..models import CarnetPedagogique
    carnet, created = CarnetPedagogique.objects.get_or_create(eleve=eleve)
    
    if request.method == 'POST':
        form = RepetitionForm(request.POST)
        if form.is_valid():
            try:
                # Utiliser une transaction pour garantir la cohérence des données
                from django.db import transaction
                with transaction.atomic():
                    repetition = form.save(commit=False)
                    repetition.carnet = carnet  # Associer au carnet et non directement à l'élève
                    repetition.save()
                    
                    # Vérifier si une répétition existe déjà pour cette sourate et cette page
                    existing = Repetition.objects.filter(
                        carnet=carnet,
                        sourate=repetition.sourate,
                        page=repetition.page
                    ).exclude(id=repetition.id).first()
                    
                    if existing:
                        # Mettre à jour la répétition existante plutôt que d'en créer une nouvelle
                        existing.nombre_repetitions += repetition.nombre_repetitions
                        existing.derniere_date = timezone.now().date()
                        existing.save()
                        repetition.delete()  # Supprimer la nouvelle répétition car on a mis à jour l'existante
                        messages.success(request, f"Répétition mise à jour avec succès. Total: {existing.nombre_repetitions} répétitions.")
                    else:
                        messages.success(request, "Répétition ajoutée avec succès.")
                        
                return redirect('carnet_pedagogique', eleve_id=eleve.id)
            except Exception as e:
                messages.error(request, f"Erreur lors de l'enregistrement de la répétition: {str(e)}")
        else:
            # Afficher les erreurs de validation du formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans le champ {field}: {error}")
    else:
        form = RepetitionForm()
    
    return render(request, 'ecole_app/carnet/ajouter_repetition.html', {
        'form': form,
        'eleve': eleve
    })

@login_required
def modifier_repetition(request, repetition_id):
    """Vue pour modifier une répétition existante"""
    repetition = get_object_or_404(Repetition, id=repetition_id)
    
    # Vérifier que la répétition a un carnet associé
    if not repetition.carnet:
        messages.error(request, "Cette répétition n'a pas de carnet pédagogique associé.")
        return redirect('dashboard')
    
    # Vérifier que le carnet a un élève associé
    if not hasattr(repetition.carnet, 'eleve') or not repetition.carnet.eleve:
        messages.error(request, "Le carnet pédagogique n'a pas d'élève associé.")
        return redirect('dashboard')
    
    # Accéder à l'élève via le carnet pédagogique
    eleve = repetition.carnet.eleve
    
    if request.method == 'POST':
        form = RepetitionForm(request.POST, instance=repetition)
        if form.is_valid():
            form.save()
            messages.success(request, "Répétition modifiée avec succès.")
            return redirect('carnet_pedagogique', eleve_id=eleve.id)
    else:
        form = RepetitionForm(instance=repetition)
    
    return render(request, 'ecole_app/carnet/modifier_repetition.html', {
        'form': form,
        'repetition': repetition,
        'eleve': eleve  # Ajouter l'élève au contexte pour le template
    })

@login_required
def supprimer_repetition(request, repetition_id):
    """Vue pour supprimer une répétition"""
    repetition = get_object_or_404(Repetition, id=repetition_id)
    
    # Vérifier que la répétition a un carnet associé
    if not repetition.carnet:
        messages.error(request, "Cette répétition n'a pas de carnet pédagogique associé.")
        repetition.delete()
        return redirect('dashboard')
    
    # Vérifier que le carnet a un élève associé
    if not hasattr(repetition.carnet, 'eleve') or not repetition.carnet.eleve:
        messages.error(request, "Le carnet pédagogique n'a pas d'élève associé.")
        repetition.delete()
        return redirect('dashboard')
    
    # Accéder à l'élève via le carnet pédagogique
    eleve_id = repetition.carnet.eleve.id
    
    repetition.delete()
    messages.success(request, "Répétition supprimée avec succès.")
    return redirect('carnet_pedagogique', eleve_id=eleve_id)

@login_required
def modifier_revision(request, revision_id):
    """Vue pour modifier une révision existante"""
    revision = get_object_or_404(Revision, id=revision_id)
    
    # Vérifier que la révision a un carnet associé
    if not revision.carnet:
        messages.error(request, "Cette révision n'a pas de carnet pédagogique associé.")
        return redirect('dashboard')
    
    # Vérifier que le carnet a un élève associé
    if not hasattr(revision.carnet, 'eleve') or not revision.carnet.eleve:
        messages.error(request, "Le carnet pédagogique n'a pas d'élève associé.")
        return redirect('dashboard')
    
    # Accéder à l'élève via le carnet pédagogique
    eleve = revision.carnet.eleve
    
    if request.method == 'POST':
        form = RevisionForm(request.POST, instance=revision)
        if form.is_valid():
            form.save()
            messages.success(request, "Révision modifiée avec succès.")
            # S'assurer que l'ID de l'élève est correctement passé
            return redirect('carnet_pedagogique', eleve_id=eleve.id)
    else:
        form = RevisionForm(instance=revision)
    
    return render(request, 'ecole_app/carnet/modifier_revision.html', {
        'form': form,
        'revision': revision,
        'eleve': eleve  # Ajouter l'élève au contexte pour le template
    })

@login_required
def supprimer_revision(request, revision_id):
    """Vue pour supprimer une révision"""
    revision = get_object_or_404(Revision, id=revision_id)
    
    # Vérifier que la révision a un carnet associé
    if not revision.carnet:
        messages.error(request, "Cette révision n'a pas de carnet pédagogique associé.")
        revision.delete()
        return redirect('dashboard')
    
    # Vérifier que le carnet a un élève associé
    if not hasattr(revision.carnet, 'eleve') or not revision.carnet.eleve:
        messages.error(request, "Le carnet pédagogique n'a pas d'élève associé.")
        revision.delete()
        return redirect('dashboard')
    
    # Accéder à l'élève via le carnet pédagogique
    eleve_id = revision.carnet.eleve.id
    
    revision.delete()
    messages.success(request, "Révision supprimée avec succès.")
    return redirect('carnet_pedagogique', eleve_id=eleve_id)

@login_required
def ajouter_revision(request, eleve_id):
    """Vue pour ajouter une révision au carnet pédagogique d'un élève"""
    eleve = get_object_or_404(Eleve, id=eleve_id)
    
    # Récupérer ou créer le carnet pédagogique de l'élève
    from ..models import CarnetPedagogique
    carnet, created = CarnetPedagogique.objects.get_or_create(eleve=eleve)
    
    if request.method == 'POST':
        form = RevisionForm(request.POST)
        if form.is_valid():
            revision = form.save(commit=False)
            revision.carnet = carnet  # Associer au carnet et non directement à l'élève
            
            # Calculer le jour de la semaine à partir de la date
            if revision.date:
                weekday = revision.date.weekday()
                days = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
                revision.jour = days[weekday]
            
            # Récupérer les champs supplémentaires du formulaire
            # Ces champs ne sont pas stockés dans le modèle Revision mais peuvent être utilisés
            # pour d'autres traitements si nécessaire
            sourate = form.cleaned_data.get('sourate')
            debut_page = form.cleaned_data.get('debut_page')
            fin_page = form.cleaned_data.get('fin_page')
            enseignant = form.cleaned_data.get('enseignant')
            remarques = form.cleaned_data.get('remarques')
            
            # Enregistrer la révision
            revision.save()
            
            messages.success(request, "Révision ajoutée avec succès.")
            return redirect('carnet_pedagogique', eleve_id=eleve.id)
    else:
        form = RevisionForm(initial={'date': timezone.now().date()})
    
    context = {
        'form': form,
        'eleve': eleve,
        'titre_page': "Ajouter une révision"
    }
    return render(request, 'ecole_app/carnet/ajouter_revision.html', context)
