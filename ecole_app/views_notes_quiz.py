from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from .models import NoteExamen, Classe
from .models_pedagogie import TentativeQuiz, Quiz
from .utils import is_professeur_or_admin

@login_required
@user_passes_test(is_professeur_or_admin)
def convertir_quiz_en_note(request, tentative_id):
    """Convertit le score d'un quiz en note d'examen"""
    # Récupérer la tentative de quiz
    tentative = get_object_or_404(TentativeQuiz, id=tentative_id)
    
    # Vérifier si la tentative est terminée
    if not tentative.terminee:
        messages.error(request, "Ce quiz n'est pas terminé et ne peut pas être converti en note.")
        return redirect('resultats_quiz_classe', quiz_id=tentative.quiz.id)
    
    # Vérifier si une note existe déjà pour cette tentative
    note_existante = NoteExamen.objects.filter(tentative_quiz=tentative).first()
    if note_existante:
        messages.info(request, f"Une note existe déjà pour cette tentative de quiz: {note_existante.note}/20")
        return redirect('modifier_note', note_id=note_existante.id)
    
    # Récupérer le score du quiz (sur 100)
    score = tentative.score
    if score is None:
        # Calculer le score si nécessaire
        score = tentative.calculer_score()
        if score is None:
            messages.error(request, "Impossible de calculer le score pour ce quiz.")
            return redirect('resultats_quiz_classe', quiz_id=tentative.quiz.id)
    
    # Convertir le score en note sur 20
    note_sur_20 = (score / 100) * 20
    
    if request.method == 'POST':
        with transaction.atomic():
            # Créer une nouvelle note d'examen
            note = NoteExamen(
                eleve=tentative.eleve,
                professeur=request.user.professeur,
                classe=tentative.eleve.classe,
                titre=f"Quiz: {tentative.quiz.titre}",
                type_examen='quiz',
                note=Decimal(str(note_sur_20)),
                note_max=20,
                date_examen=timezone.now().date(),
                quiz=tentative.quiz,
                tentative_quiz=tentative,
                commentaire=f"Note générée automatiquement à partir du quiz '{tentative.quiz.titre}'. Score: {score}%"
            )
            note.save()
            
            messages.success(request, f"Note créée avec succès: {note_sur_20:.2f}/20")
            return redirect('liste_notes_professeur')
    
    # Afficher le formulaire de confirmation
    context = {
        'tentative': tentative,
        'score': score,
        'note_sur_20': note_sur_20,
    }
    return render(request, 'ecole_app/notes/convertir_quiz_en_note.html', context)

@login_required
def historique_quiz_avec_notes(request):
    """Affiche l'historique des quiz avec les notes associées pour un élève"""
    eleve = request.user.eleve
    
    # Récupérer toutes les tentatives de quiz de l'élève
    tentatives = TentativeQuiz.objects.filter(
        eleve=eleve,
        terminee=True
    ).select_related('quiz', 'quiz__module').order_by('-date_debut')
    
    # Récupérer les notes associées aux tentatives
    for tentative in tentatives:
        tentative.note_associee = NoteExamen.objects.filter(tentative_quiz=tentative).first()
    
    context = {
        'tentatives': tentatives,
    }
    return render(request, 'ecole_app/notes/historique_quiz_notes.html', context)

@login_required
@user_passes_test(is_professeur_or_admin)
def liste_tentatives_quiz_classe(request, classe_id):
    """Liste toutes les tentatives de quiz pour une classe donnée"""
    classe = get_object_or_404(Classe, id=classe_id)
    
    # Vérifier que le professeur est bien associé à cette classe
    if not request.user.is_staff and request.user.professeur not in classe.professeurs.all():
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('dashboard')
    
    # Récupérer toutes les tentatives de quiz pour les élèves de cette classe
    tentatives = TentativeQuiz.objects.filter(
        eleve__classe=classe,
        terminee=True
    ).select_related('eleve', 'quiz').order_by('-date_debut')
    
    # Récupérer les notes associées aux tentatives
    for tentative in tentatives:
        tentative.note_associee = NoteExamen.objects.filter(tentative_quiz=tentative).first()
    
    context = {
        'classe': classe,
        'tentatives': tentatives,
    }
    return render(request, 'ecole_app/notes/liste_tentatives_quiz_classe.html', context)
