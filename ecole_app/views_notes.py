from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from .models import NoteExamen, Eleve, Classe, Professeur, Composante
from .forms import NoteExamenForm
from datetime import date

@login_required
def liste_notes_professeur(request):
    """Vue pour lister les notes créées par le professeur connecté ou accessible par l'admin"""
    # Vérifier si l'utilisateur est un professeur ou un admin
    is_admin = request.user.is_superuser or request.user.is_staff
    is_professeur = hasattr(request.user, 'professeur')
    
    if not (is_admin or is_professeur):
        messages.error(request, "Accès réservé aux professeurs et administrateurs.")
        return redirect('dashboard')
    
    composante_id = request.session.get('composante_id')
    
    if not composante_id:
        messages.warning(request, "Veuillez sélectionner une composante.")
        return redirect('selection_composante')
    
    # Différent traitement selon le type d'utilisateur
    if is_admin:
        # Pour les admins, afficher toutes les notes de la composante sélectionnée
        notes = NoteExamen.objects.filter(
            classe__composante_id=composante_id
        ).select_related('eleve', 'classe', 'professeur').order_by('-date_examen', '-date_creation')
        
        # Récupérer toutes les classes de la composante pour le filtre
        classes = Classe.objects.filter(composante_id=composante_id).order_by('nom')
        
        # Récupérer tous les élèves de la composante pour le filtre
        eleves = Eleve.objects.filter(
            classes__composante_id=composante_id,
            archive=False
        ).distinct().order_by('nom', 'prenom')
    else:
        # Pour les professeurs, afficher uniquement leurs notes
        professeur = request.user.professeur
        
        # Récupérer les notes du professeur avec optimisation des requêtes
        notes = NoteExamen.objects.filter(
            professeur=professeur,
            classe__composante_id=composante_id
        ).select_related('eleve', 'classe').order_by('-date_examen', '-date_creation')
        
        # Récupérer les classes du professeur pour le filtre
        classes = professeur.classes.filter(composante_id=composante_id).order_by('nom')
        
        # Récupérer TOUS les élèves des classes du professeur pour le filtre
        eleves = Eleve.objects.filter(
            classes__in=professeur.classes.all(),
            archive=False
        ).distinct().order_by('nom', 'prenom')
    
    # Filtrage par classe
    classe_id = request.GET.get('classe')
    if classe_id:
        notes = notes.filter(classe_id=classe_id)
    
    # Filtrage par élève
    eleve_id = request.GET.get('eleve')
    if eleve_id:
        notes = notes.filter(eleve_id=eleve_id)
    
    context = {
        'notes': notes,
        'classes': classes,
        'eleves': eleves,
        'classe_selectionnee': classe_id,
        'eleve_selectionne': eleve_id,
    }
    
    return render(request, 'ecole_app/notes/liste.html', context)

@login_required
def ajouter_note(request):
    """Vue pour ajouter une note d'examen"""
    # Vérifier si l'utilisateur est un professeur ou un admin
    is_admin = request.user.is_superuser or request.user.is_staff
    is_professeur = hasattr(request.user, 'professeur')
    
    if not (is_admin or is_professeur):
        messages.error(request, "Accès réservé aux professeurs et administrateurs.")
        return redirect('dashboard')
    
    # Pour les admins, on utilise automatiquement un professeur nommé "administration"
    if is_admin:
        # Chercher ou créer un professeur nommé "administration"
        professeur, created = Professeur.objects.get_or_create(
            nom="administration",
            defaults={
                'email': request.user.email if hasattr(request.user, 'email') else None
            }
        )
        
        # Si le professeur vient d'être créé, s'assurer qu'il est associé à toutes les composantes
        if created:
            composantes = Composante.objects.all()
            professeur.composantes.add(*composantes)
            professeur.save()
            
        professeurs = None  # Pas besoin de la liste des professeurs
    else:
        professeur = request.user.professeur
        professeurs = None
    composante_id = request.session.get('composante_id')
    
    if not composante_id:
        messages.warning(request, "Veuillez sélectionner une composante.")
        return redirect('selection_composante')
    
    if request.method == 'POST':
        form = NoteExamenForm(request.POST, professeur=professeur, composante_id=composante_id)
        if form.is_valid():
            note = form.save(commit=False)
            note.professeur = professeur
            note.save()
            messages.success(request, f"Note ajoutée avec succès pour {note.eleve}.")
            return redirect('liste_notes_professeur')
    else:
        form = NoteExamenForm(professeur=professeur, composante_id=composante_id)
    
    context = {
        'form': form,
    }
    
    # Ajouter les professeurs au contexte si l'utilisateur est admin
    if is_admin:
        context['professeurs'] = professeurs
        context['professeur_id'] = professeur.id if professeur else None
    
    return render(request, 'ecole_app/notes/ajouter.html', context)

@login_required
def modifier_note(request, note_id):
    """Vue pour modifier une note d'examen"""
    # Vérifier si l'utilisateur est un professeur ou un admin
    is_admin = request.user.is_superuser or request.user.is_staff
    is_professeur = hasattr(request.user, 'professeur')
    
    if not (is_admin or is_professeur):
        messages.error(request, "Accès réservé aux professeurs et administrateurs.")
        return redirect('dashboard')
    
    # Récupération de la note selon le type d'utilisateur
    if is_admin:
        note = get_object_or_404(NoteExamen, id=note_id)
        professeur = note.professeur
    else:
        professeur = request.user.professeur
        note = get_object_or_404(NoteExamen, id=note_id, professeur=professeur)
    
    if request.method == 'POST':
        form = NoteExamenForm(request.POST, instance=note, professeur=professeur, composante_id=note.classe.composante.id)
        if form.is_valid():
            form.save()
            messages.success(request, f"Note modifiée avec succès pour {note.eleve}.")
            return redirect('liste_notes_professeur')
    else:
        form = NoteExamenForm(instance=note, professeur=professeur, composante_id=note.classe.composante.id)
    
    context = {
        'form': form,
        'note': note,
        'is_admin': is_admin
    }
    
    return render(request, 'ecole_app/notes/modifier.html', context)

@login_required
def supprimer_note(request, note_id):
    """Vue pour supprimer une note d'examen"""
    # Vérifier si l'utilisateur est un professeur ou un admin
    is_admin = request.user.is_superuser or request.user.is_staff
    is_professeur = hasattr(request.user, 'professeur')
    
    if not (is_admin or is_professeur):
        messages.error(request, "Accès réservé aux professeurs et administrateurs.")
        return redirect('dashboard')
    
    # Récupération de la note selon le type d'utilisateur
    if is_admin:
        note = get_object_or_404(NoteExamen, id=note_id)
    else:
        professeur = request.user.professeur
        note = get_object_or_404(NoteExamen, id=note_id, professeur=professeur)
    
    if request.method == 'POST':
        eleve_nom = str(note.eleve)
        note.delete()
        messages.success(request, f"Note supprimée avec succès pour {eleve_nom}.")
        return redirect('liste_notes_professeur')
    
    context = {
        'note': note,
        'is_admin': is_admin
    }
    
    return render(request, 'ecole_app/notes/supprimer.html', context)

@login_required
def statistiques_notes_classe(request, classe_id):
    """Vue pour afficher les statistiques des notes d'une classe"""
    # Vérifier si l'utilisateur est un professeur ou un admin
    is_admin = request.user.is_superuser or request.user.is_staff
    is_professeur = hasattr(request.user, 'professeur')
    
    if not (is_admin or is_professeur):
        messages.error(request, "Accès réservé aux professeurs et administrateurs.")
        return redirect('dashboard')
    
    # Récupération de la classe selon le type d'utilisateur
    if is_admin:
        classe = get_object_or_404(Classe, id=classe_id)
    else:
        professeur = request.user.professeur
        classe = get_object_or_404(Classe, id=classe_id, professeur=professeur)
    
    # Récupérer toutes les notes de la classe
    notes = NoteExamen.objects.filter(classe=classe).select_related('eleve')
    
    # Calculer les statistiques
    stats = {
        'total_notes': notes.count(),
        'moyenne_classe': notes.aggregate(Avg('note'))['note__avg'] or 0,
        'notes_par_type': {},
        'notes_par_eleve': {}
    }
    
    # Statistiques par type d'examen
    for type_code, type_nom in NoteExamen.TYPE_EXAMEN_CHOICES:
        notes_type = notes.filter(type_examen=type_code)
        if notes_type.exists():
            stats['notes_par_type'][type_nom] = {
                'count': notes_type.count(),
                'moyenne': notes_type.aggregate(Avg('note'))['note__avg'] or 0
            }
    
    # Statistiques par élève (ForeignKey et ManyToMany)
    eleves_fk = classe.eleves.filter(archive=False)
    eleves_m2m = classe.eleves_multi.filter(archive=False)
    eleves = (eleves_fk | eleves_m2m).distinct().order_by('nom', 'prenom')
    for eleve in eleves:
        notes_eleve = notes.filter(eleve=eleve)
        if notes_eleve.exists():
            stats['notes_par_eleve'][eleve.id] = {
                'eleve': eleve,
                'count': notes_eleve.count(),
                'moyenne': notes_eleve.aggregate(Avg('note'))['note__avg'] or 0,
                'derniere_note': notes_eleve.order_by('-date_examen').first()
            }
    
    context = {
        'classe': classe,
        'stats': stats,
        'notes': notes.order_by('-date_examen')[:10]  # Les 10 dernières notes
    }
    
    # Ajouter le statut admin au contexte
    context['is_admin'] = is_admin
    
    # Utiliser le template sans barre latérale pour les professeurs
    if is_professeur and not is_admin:
        return render(request, 'ecole_app/notes/statistiques_classe_fullscreen.html', context)
    else:
        return render(request, 'ecole_app/notes/statistiques.html', context)

@login_required
def mes_notes(request):
    """Vue pour qu'un élève puisse voir ses notes d'examen"""
    # Vérifier si l'utilisateur est un élève
    if not hasattr(request.user, 'eleve'):
        messages.error(request, "Accès réservé aux élèves.")
        return redirect('dashboard')
    
    eleve = request.user.eleve
    
    # Récupérer toutes les notes de l'élève avec optimisation des requêtes
    notes = NoteExamen.objects.filter(
        eleve=eleve
    ).select_related('professeur', 'classe').order_by('-date_examen', '-date_creation')
    
    # Calculer les statistiques
    stats = {
        'total_notes': notes.count(),
        'moyenne_generale': notes.aggregate(Avg('note'))['note__avg'] or 0,
        'notes_par_type': {},
        'derniere_note': notes.first() if notes.exists() else None
    }
    
    # Statistiques par type d'examen
    for type_code, type_nom in NoteExamen.TYPE_EXAMEN_CHOICES:
        notes_type = notes.filter(type_examen=type_code)
        if notes_type.exists():
            stats['notes_par_type'][type_nom] = {
                'count': notes_type.count(),
                'moyenne': notes_type.aggregate(Avg('note'))['note__avg'] or 0
            }
    
    context = {
        'eleve': eleve,
        'notes': notes[:10],  # Les 10 dernières notes
        'stats': stats,
    }
    
    return render(request, 'ecole_app/notes/mes_notes_eleve.html', context)

@login_required
def historique_quiz_eleve(request):
    """Vue pour qu'un élève puisse voir l'historique de tous ses quiz"""
    # Vérifier si l'utilisateur est un élève
    if not hasattr(request.user, 'eleve'):
        messages.error(request, "Accès réservé aux élèves.")
        return redirect('dashboard')
    
    eleve = request.user.eleve
    
    # Import ici pour éviter les imports circulaires
    from .models_pedagogie import TentativeQuiz, Reponse
    
    # Récupérer toutes les tentatives de quiz de l'élève
    tentatives = TentativeQuiz.objects.filter(
        eleve=eleve
    ).select_related('quiz', 'quiz__module', 'quiz__module__professeur').order_by('-date_fin')
    
    # Calculer les statistiques
    stats = {
        'total_quiz': tentatives.count(),
        'score_moyen': tentatives.aggregate(Avg('score'))['score__avg'] or 0,
        'dernier_quiz': tentatives.first() if tentatives.exists() else None
    }
    
    context = {
        'eleve': eleve,
        'tentatives': tentatives,
        'stats': stats,
    }
    
    return render(request, 'ecole_app/notes/historique_quiz.html', context)
