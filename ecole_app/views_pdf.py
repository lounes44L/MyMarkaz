from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models_pedagogie import TentativeQuiz
from .utils import render_to_pdf

@login_required
def telecharger_resultats_quiz_pdf(request, tentative_id):
    """Génère un PDF avec les résultats du quiz"""
    # Récupérer la tentative
    if hasattr(request.user, 'eleve'):
        # Si c'est un élève, il ne peut voir que ses propres résultats
        tentative = get_object_or_404(TentativeQuiz, id=tentative_id, eleve=request.user.eleve)
    elif hasattr(request.user, 'professeur'):
        # Si c'est un professeur, il peut voir les résultats de ses élèves
        tentative = get_object_or_404(TentativeQuiz, id=tentative_id, quiz__module__professeur=request.user.professeur)
    else:
        # Si c'est un admin, il peut voir tous les résultats
        tentative = get_object_or_404(TentativeQuiz, id=tentative_id)
    
    # Récupérer les réponses avec les questions et les réponses correctes
    reponses_eleve = tentative.reponses.all().select_related('question')
    
    # Préparer les données pour l'affichage
    resultats = []
    for reponse in reponses_eleve:
        question = reponse.question
        choix_selectionnes = list(reponse.choix_selectionnes.all())
        choix_corrects = list(question.choix.filter(est_correct=True))
        
        # Créer un dictionnaire avec toutes les informations nécessaires
        resultat = {
            'question': question,
            'reponse': reponse,
            'choix_selectionnes': choix_selectionnes,
            'choix_corrects': choix_corrects,
        }
        resultats.append(resultat)
    
    # Générer le nom du fichier PDF
    filename = f"quiz_{tentative.quiz.titre.replace(' ', '_')}_{tentative.eleve.nom}_{tentative.eleve.prenom}_{timezone.now().strftime('%Y%m%d')}.pdf"
    
    # Préparer le contexte pour le template PDF
    context = {
        'tentative': tentative,
        'resultats': resultats,
        'date_generation': timezone.now(),
    }
    
    # Générer le PDF
    pdf = render_to_pdf('ecole_app/cours_quiz/pdf_resultats_quiz.html', context)
    
    # Configurer la réponse HTTP pour le téléchargement
    if pdf:
        response = pdf
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    # En cas d'erreur, rediriger vers la page des résultats
    return redirect('resultats_quiz', tentative_id=tentative_id)
