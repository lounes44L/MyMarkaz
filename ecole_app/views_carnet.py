from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Count, Sum, Avg
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import (Eleve, Professeur, CarnetPedagogique, EcouteAvantMemo, 
                    Memorisation, Revision, Repetition, Creneau, CompetenceLivre, EvaluationCompetence)
from .forms import (CarnetPedagogiqueForm, EcouteAvantMemoForm, MemorisationForm,
                    RevisionForm, RepetitionForm)

def check_eleve_access(request, eleve_id=None):
    """Vérifier si l'utilisateur a accès à l'élève spécifié"""
    # Si c'est un élève connecté, il ne peut accéder qu'à son propre carnet
    if hasattr(request.user, 'eleve'):
        if eleve_id and str(request.user.eleve.id) != str(eleve_id):
            return None, False
        return request.user.eleve, True
    
    # Si c'est un professeur, il ne peut accéder qu'aux élèves de ses créneaux
    elif hasattr(request.user, 'professeur') and eleve_id:
        eleve = get_object_or_404(Eleve, id=eleve_id)
        # Récupérer les classes du professeur
        classes_prof = request.user.professeur.classes.all()
        # Récupérer les créneaux associés à ces classes
        creneaux_prof = Creneau.objects.filter(classes__in=classes_prof).distinct()
        # Vérifier si l'élève est dans l'une des classes du professeur
        eleve_classes = eleve.classes.all()
        prof_classes = request.user.professeur.classes.all()
        
        # Vérifier s'il y a une intersection entre les classes de l'élève et celles du professeur
        if eleve_classes.filter(id__in=prof_classes).exists() or request.user.is_staff:
            return eleve, True
        return None, False
    
    # Si c'est un administrateur, il peut accéder à tous les élèves
    elif request.user.is_staff and eleve_id:
        return get_object_or_404(Eleve, id=eleve_id), True
    
    return None, False

@login_required
def carnet_pedagogique(request, eleve_id=None):
    """Vue principale du carnet pédagogique"""
    # Si c'est un élève connecté, afficher son propre carnet
    if hasattr(request.user, 'eleve') and not eleve_id:
        eleve = request.user.eleve
    # Sinon vérifier les permissions d'accès
    else:
        eleve, has_access = check_eleve_access(request, eleve_id)
        if not has_access:
            messages.error(request, "Vous n'avez pas accès au carnet de cet élève.")
            return redirect('dashboard')
    
    # Récupérer ou créer le carnet pédagogique de l'élève
    carnet, created = CarnetPedagogique.objects.get_or_create(eleve=eleve)
    
    # Récupérer le mois et l'année depuis les paramètres GET ou utiliser la date actuelle
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
    
    # Récupérer les données du carnet
    ecoutes = EcouteAvantMemo.objects.filter(carnet=carnet).order_by('-date')
    memorisations = Memorisation.objects.filter(carnet=carnet).order_by('-date')
    
    # Utiliser values() pour sélectionner uniquement les champs nécessaires et éviter l'erreur de colonne manquante
    revisions = Revision.objects.filter(carnet=carnet).values('id', 'carnet_id', 'semaine', 'date', 'jour', 'nombre_hizb').order_by('-date')
    repetitions = Repetition.objects.filter(carnet=carnet).order_by('-derniere_date')
    
    # Statistiques
    total_pages_memo = memorisations.aggregate(Sum('fin_page'))['fin_page__sum'] or 0
    
    # Récupérer les compétences du livre et leurs évaluations
    competences = CompetenceLivre.objects.all().order_by('lecon', 'ordre')
    evaluations = EvaluationCompetence.objects.filter(eleve=eleve).select_related('competence')
    
    # Créer un dictionnaire des évaluations par competence_id pour un accès plus rapide
    evaluations_dict = {eval.competence_id: eval for eval in evaluations}
    
    # Organiser les compétences par leçon avec leurs évaluations
    competences_par_lecon = {}
    competences_status = {}
    
    for competence in competences:
        if competence.lecon not in competences_par_lecon:
            competences_par_lecon[competence.lecon] = []
        
        # Récupérer l'évaluation pour cette compétence
        evaluation = evaluations_dict.get(competence.id)
        
        # Ajouter le statut de la compétence au dictionnaire
        if evaluation:
            competences_status[str(competence.id)] = evaluation.statut
        
        competences_par_lecon[competence.lecon].append({
            'competence': competence,
            'evaluation': evaluation
        })
    
    context = {
        'eleve': eleve,
        'carnet': carnet,
        'ecoutes': ecoutes,
        'memorisations': memorisations,
        'revisions': revisions,
        'repetitions': repetitions,
        'total_pages_memo': total_pages_memo,
        'competences_par_lecon': competences_par_lecon,
        'competences_status': competences_status,
        'mois': mois,
        'annee': annee,
        'mois_actuel': date_actuelle.month,  # Mois actuel pour le bouton "Mois courant"
        'annee_actuelle': date_actuelle.year,  # Année actuelle pour le bouton "Mois courant"
    }
    return render(request, 'ecole_app/carnet/index.html', context)

@login_required
def ajouter_ecoute(request, eleve_id=None):
    """Ajouter une séance d'écoute avant mémorisation"""
    # Vérifier les permissions d'accès
    eleve, has_access = check_eleve_access(request, eleve_id)
    if not has_access:
        messages.error(request, "Vous n'avez pas accès au carnet de cet élève.")
        return redirect('dashboard')
    
    carnet, created = CarnetPedagogique.objects.get_or_create(eleve=eleve)
    
    if request.method == 'POST':
        form = EcouteAvantMemoForm(request.POST)
        if form.is_valid():
            ecoute = form.save(commit=False)
            ecoute.carnet = carnet
            ecoute.save()
            messages.success(request, "Séance d'écoute ajoutée avec succès.")
            return redirect('carnet_pedagogique', eleve_id=eleve.id)
    else:
        form = EcouteAvantMemoForm()
        # Pré-remplir l'enseignant si c'est un professeur connecté
        if hasattr(request.user, 'professeur'):
            form.initial['enseignant'] = request.user.professeur
    
    context = {
        'form': form,
        'eleve': eleve,
        'titre_page': "Ajouter une séance d'écoute"
    }
    return render(request, 'ecole_app/carnet/formulaire.html', context)

@login_required
def ajouter_memorisation(request, eleve_id=None):
    """Ajouter une séance de mémorisation"""
    # Vérifier les permissions d'accès
    eleve, has_access = check_eleve_access(request, eleve_id)
    if not has_access:
        messages.error(request, "Vous n'avez pas accès au carnet de cet élève.")
        return redirect('dashboard')
    
    carnet, created = CarnetPedagogique.objects.get_or_create(eleve=eleve)
    
    if request.method == 'POST':
        form = MemorisationForm(request.POST)
        if form.is_valid():
            memorisation = form.save(commit=False)
            memorisation.carnet = carnet
            # Récupérer le nom de la sourate depuis les données nettoyées
            if 'sourate' in form.cleaned_data and form.cleaned_data['sourate']:
                memorisation.sourate = form.cleaned_data['sourate']
            memorisation.save()
            messages.success(request, "Séance de mémorisation ajoutée avec succès.")
            return redirect('carnet_pedagogique', eleve_id=eleve.id)
    else:
        form = MemorisationForm()
        # Pré-remplir l'enseignant si c'est un professeur connecté
        if hasattr(request.user, 'professeur'):
            form.initial['enseignant'] = request.user.professeur
    
    context = {
        'form': form,
        'eleve': eleve,
        'titre_page': "Ajouter une séance de mémorisation"
    }
    return render(request, 'ecole_app/carnet/formulaire.html', context)

@login_required
def ajouter_revision(request, eleve_id=None):
    """Ajouter une révision"""
    # Vérifier les permissions d'accès
    eleve, has_access = check_eleve_access(request, eleve_id)
    if not has_access:
        messages.error(request, "Vous n'avez pas accès au carnet de cet élève.")
        return redirect('dashboard')
    
    carnet, created = CarnetPedagogique.objects.get_or_create(eleve=eleve)
    
    if request.method == 'POST':
        form = RevisionForm(request.POST)
        if form.is_valid():
            revision = form.save(commit=False)
            revision.carnet = carnet
            # Ignorer le champ remarques pour éviter l'erreur de colonne manquante
            # remarques = form.cleaned_data.get('remarques')
            # if remarques:
            #     revision.remarques = remarques
            # Auto-calculate the week number
            revision.semaine = revision.date.isocalendar()[1]
            revision.save()
            messages.success(request, "Révision ajoutée avec succès.")
            return redirect('carnet_pedagogique', eleve_id=eleve.id)
    else:
        # Pré-remplir la semaine actuelle
        semaine_actuelle = timezone.now().isocalendar()[1]  # Numéro de la semaine dans l'année
        form = RevisionForm(initial={'semaine': semaine_actuelle})
    
    context = {
        'form': form,
        'eleve': eleve,
        'titre_page': "Ajouter une révision"
    }
    return render(request, 'ecole_app/carnet/formulaire.html', context)

@login_required
def ajouter_repetition(request, eleve_id=None):
    """Ajouter une répétition"""
    # Vérifier les permissions d'accès
    eleve, has_access = check_eleve_access(request, eleve_id)
    if not has_access:
        messages.error(request, "Vous n'avez pas accès au carnet de cet élève.")
        return redirect('dashboard')
    
    carnet, created = CarnetPedagogique.objects.get_or_create(eleve=eleve)
    
    if request.method == 'POST':
        form = RepetitionForm(request.POST)
        if form.is_valid():
            # Vérifier si une répétition existe déjà pour cette sourate/page
            sourate = form.cleaned_data['sourate']
            page = form.cleaned_data['page']
            nombre = form.cleaned_data['nombre_repetitions']
            
            repetition, created = Repetition.objects.get_or_create(
                carnet=carnet,
                sourate=sourate,
                page=page,
                defaults={'nombre_repetitions': nombre}
            )
            
            if not created:
                # Si la répétition existait déjà, ajouter le nombre
                repetition.nombre_repetitions += nombre
                repetition.save()
            
            messages.success(request, "Répétition ajoutée avec succès.")
            return redirect('carnet_pedagogique', eleve_id=eleve.id)
    else:
        form = RepetitionForm()
    
    context = {
        'form': form,
        'eleve': eleve,
        'titre_page': "Ajouter une répétition"
    }
    return render(request, 'ecole_app/carnet/formulaire.html', context)

@login_required
@require_http_methods(["POST"])
def evaluation_competences_batch(request):
    """Enregistrer plusieurs évaluations de compétences en lot via AJAX"""
    try:
        data = json.loads(request.body)
        competences_data = data.get('competences', [])
        date_annotation = data.get('date_annotation')
        
        if not competences_data:
            return JsonResponse({'success': False, 'error': 'Aucune compétence fournie'})
        
        # Vérifier l'accès à l'élève
        eleve_id = competences_data[0].get('eleve_id')
        if not eleve_id:
            return JsonResponse({'success': False, 'error': 'ID élève manquant'})
            
        eleve, has_access = check_eleve_access(request, eleve_id)
        if not has_access:
            return JsonResponse({'success': False, 'error': 'Accès non autorisé'})
        
        # Traiter chaque compétence
        evaluations_created = 0
        for comp_data in competences_data:
            competence_id = comp_data.get('competence_id')
            statut = comp_data.get('statut')
            
            if not competence_id or not statut:
                continue
                
            try:
                # Chercher la compétence
                competence = CompetenceLivre.objects.get(id=competence_id)
                
                # Convertir la date si elle est fournie sous forme de string
                if date_annotation and isinstance(date_annotation, str):
                    from datetime import datetime
                    try:
                        date_eval = datetime.strptime(date_annotation, '%Y-%m-%d').date()
                    except ValueError:
                        date_eval = timezone.now().date()
                else:
                    date_eval = date_annotation if date_annotation else timezone.now().date()
                
                # Créer ou mettre à jour l'évaluation
                evaluation, created = EvaluationCompetence.objects.update_or_create(
                    eleve=eleve,
                    competence=competence,
                    defaults={
                        'statut': statut,
                        'date_evaluation': date_eval
                    }
                )
                evaluations_created += 1
                
            except CompetenceLivre.DoesNotExist:
                continue
        
        return JsonResponse({
            'success': True, 
            'message': f'{evaluations_created} évaluations enregistrées avec succès'
        })
        
    except json.JSONDecodeError as e:
        return JsonResponse({'success': False, 'error': f'Données JSON invalides: {str(e)}'})
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return JsonResponse({'success': False, 'error': f'Erreur serveur: {str(e)}', 'details': error_details})
