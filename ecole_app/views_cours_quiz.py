from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q

from .models import (
    CoursPartage,
    Professeur, Eleve, Classe
)
from .models_pedagogie import Quiz, Question, TentativeQuiz, Reponse, Choix
from .views_auth import is_professeur, is_eleve, is_admin

# Fonction pour vérifier si l'utilisateur est un professeur ou un administrateur
def is_professeur_or_admin(user):
    """Vérifie si l'utilisateur est un professeur ou un administrateur"""
    return is_professeur(user) or is_admin(user)

# Vues pour les cours partagés

@login_required
@user_passes_test(is_professeur_or_admin)
def liste_cours_professeur(request):
    """Affiche la liste des cours partagés par le professeur connecté ou tous les cours pour un admin"""
    if is_admin(request.user) and not hasattr(request.user, 'professeur'):
        # Si c'est un admin, montrer tous les cours
        cours = CoursPartage.objects.all().order_by('-date_creation')
        context = {
            'cours': cours,
            'is_admin': True
        }
        return render(request, 'ecole_app/cours_quiz/liste_cours_professeur.html', context)
    
    # Si c'est un professeur
    professeur = request.user.professeur
    
    # Vérifier si le professeur enseigne dans plusieurs composantes
    if professeur.composantes.count() > 1:
        # Vérifier si une composante est sélectionnée dans la session
        composante_id = request.session.get('composante_id')
        if not composante_id:
            messages.info(request, 'Veuillez sélectionner une composante pour voir vos cours.')
            return redirect('selection_composante')
    
    cours = CoursPartage.objects.filter(professeur=professeur).order_by('-date_creation')
    
    context = {
        'cours': cours,
    }
    return render(request, 'ecole_app/cours_quiz/liste_cours_professeur.html', context)

@login_required
@user_passes_test(is_professeur_or_admin)
def ajouter_cours(request):
    """Permet à un professeur ou un admin d'ajouter un nouveau cours partagé"""
    # Vérifier si l'utilisateur est un admin
    is_user_admin = is_admin(request.user) and not hasattr(request.user, 'professeur')
    
    if is_user_admin:
        # Si c'est un admin, montrer toutes les classes
        classes = Classe.objects.all()
        professeur = None
    else:
        # Si c'est un professeur
        professeur = request.user.professeur
        classes = Classe.objects.filter(professeur=professeur)
    
    if request.method == 'POST':
        titre = request.POST.get('titre')
        description = request.POST.get('description')
        fichier = request.FILES.get('fichier')
        classes_ids = request.POST.getlist('classes')
        
        if not titre or not fichier:
            messages.error(request, 'Le titre et le fichier sont obligatoires.')
            return redirect('ajouter_cours')
        
        cours = CoursPartage(
            titre=titre,
            description=description,
            fichier=fichier,
            professeur=None if is_user_admin else professeur,
            eleve=None  # Rendre le champ 'eleve' explicitement optionnel
        )
        cours.save()
        
        # Ajouter les classes sélectionnées
        for classe_id in classes_ids:
            cours.classes.add(classe_id)
        
        messages.success(request, 'Le cours a été ajouté avec succès.')
        return redirect('liste_cours_professeur')
    
    context = {
        'classes': classes,
    }
    return render(request, 'ecole_app/cours_quiz/ajouter_cours.html', context)

@login_required
@user_passes_test(is_professeur_or_admin)
def modifier_cours(request, cours_id):
    """Permet à un professeur ou un admin de modifier un cours partagé"""
    # Vérifier si l'utilisateur est un admin
    is_user_admin = is_admin(request.user) and not hasattr(request.user, 'professeur')
    
    if is_user_admin:
        # Si c'est un admin, il peut modifier n'importe quel cours
        cours = get_object_or_404(CoursPartage, id=cours_id)
        classes = Classe.objects.all()
        professeur = None
    else:
        # Si c'est un professeur
        professeur = request.user.professeur
        cours = get_object_or_404(CoursPartage, id=cours_id, professeur=professeur)
        classes = Classe.objects.filter(professeur=professeur)
    
    if request.method == 'POST':
        titre = request.POST.get('titre')
        description = request.POST.get('description')
        fichier = request.FILES.get('fichier')
        classes_ids = request.POST.getlist('classes')
        
        if not titre:
            messages.error(request, 'Le titre est obligatoire.')
            return redirect('modifier_cours', cours_id=cours.id)
        
        cours.titre = titre
        cours.description = description
        if fichier:
            cours.fichier = fichier
        cours.save()
        
        # Mettre à jour les classes
        cours.classes.clear()
        for classe_id in classes_ids:
            cours.classes.add(classe_id)
        
        messages.success(request, 'Le cours a été modifié avec succès.')
        return redirect('liste_cours_professeur')
    
    context = {
        'cours': cours,
        'classes': classes,
        'classes_selectionnees': [c.id for c in cours.classes.all()],
    }
    return render(request, 'ecole_app/cours_quiz/modifier_cours.html', context)

@login_required
@user_passes_test(is_professeur_or_admin)
def supprimer_cours(request, cours_id):
    """Permet à un professeur ou un admin de supprimer un cours partagé"""
    # Vérifier si l'utilisateur est un admin
    is_user_admin = is_admin(request.user) and not hasattr(request.user, 'professeur')
    
    if is_user_admin:
        # Si c'est un admin, il peut supprimer n'importe quel cours
        cours = get_object_or_404(CoursPartage, id=cours_id)
    else:
        # Si c'est un professeur
        professeur = request.user.professeur
        cours = get_object_or_404(CoursPartage, id=cours_id, professeur=professeur)
    
    if request.method == 'POST':
        cours.delete()
        messages.success(request, 'Le cours a été supprimé avec succès.')
        return redirect('liste_cours_professeur')
    
    context = {
        'cours': cours,
    }
    return render(request, 'ecole_app/cours_quiz/supprimer_cours.html', context)

@login_required
def liste_cours_eleve(request):
    """Affiche la liste des cours partagés disponibles pour l'élève connecté"""
    eleve = request.user.eleve
    # Récupérer les cours partagés pour les classes de l'élève
    cours = CoursPartage.objects.filter(classes__in=eleve.classes.all()).distinct().order_by('-date_creation')
    
    context = {
        'cours': cours,
    }
    return render(request, 'ecole_app/cours_quiz/liste_cours_eleve.html', context)

@login_required
def telecharger_cours(request, cours_id):
    """Permet à un élève de télécharger un cours partagé"""
    eleve = request.user.eleve
    # Vérifier que le cours existe et que l'élève a accès à ce cours
    cours = get_object_or_404(CoursPartage, id=cours_id, classes__in=eleve.classes.all())
    
    # Renvoyer le fichier pour téléchargement
    if cours.fichier:
        response = HttpResponse(cours.fichier, content_type='application/force-download')
        response['Content-Disposition'] = f'attachment; filename="{cours.fichier.name.split("/")[-1]}"'
        return response
    else:
        messages.error(request, 'Ce cours ne contient pas de fichier à télécharger.')
        return redirect('liste_cours_eleve')

# Vues pour les quiz

@login_required
@user_passes_test(is_professeur_or_admin)
def liste_quiz_professeur(request):
    """Affiche la liste des quiz créés par le professeur connecté ou tous les quiz pour un admin"""
    # Vérifier si l'utilisateur est un admin
    is_user_admin = is_admin(request.user) and not hasattr(request.user, 'professeur')
    
    if is_user_admin:
        # Si c'est un admin, montrer tous les quiz
        quiz = Quiz.objects.all().prefetch_related('module__classes').order_by('-date_creation')
    else:
        # Si c'est un professeur
        professeur = request.user.professeur
        quiz = Quiz.objects.filter(module__professeur=professeur).prefetch_related('module__classes').order_by('-date_creation')
    
    context = {
        'quiz': quiz,
    }
    return render(request, 'ecole_app/cours_quiz/liste_quiz_professeur.html', context)

@login_required
@user_passes_test(is_professeur_or_admin)
def creer_quiz(request):
    """Permet à un professeur ou un admin de créer un nouveau quiz"""
    # Vérifier si l'utilisateur est un admin
    is_user_admin = is_admin(request.user) and not hasattr(request.user, 'professeur')
    
    if is_user_admin:
        # Si c'est un admin, montrer toutes les classes
        classes = Classe.objects.all()
        professeur = None
    else:
        # Si c'est un professeur
        professeur = request.user.professeur
        classes = Classe.objects.filter(professeur=professeur)
    
    # Import Module model
    from .models_pedagogie import Module
    
    if request.method == 'POST':
        titre = request.POST.get('titre')
        description = request.POST.get('description')
        classes_ids = request.POST.getlist('classes')
        temps_limite = request.POST.get('temps_limite')
        
        if not titre:
            messages.error(request, 'Le titre est obligatoire.')
            return redirect('creer_quiz')
        
        # Créer d'abord un module pour ce quiz
        module = Module.objects.create(
            titre=f"Module - {titre}",
            description=f"Module créé automatiquement pour le quiz: {titre}",
            professeur=None if is_user_admin else professeur,
            publie=True
        )
        
        # Ajouter les classes sélectionnées au module
        for classe_id in classes_ids:
            module.classes.add(classe_id)
        
        # Créer le quiz associé au module
        quiz = Quiz.objects.create(
            module=module,
            titre=titre,
            description=description,
            temps_limite=int(temps_limite) if temps_limite else None,
            publie=True
        )
        
        messages.success(request, 'Le quiz a été créé avec succès. Ajoutez maintenant des questions.')
        return redirect('ajouter_questions', quiz_id=quiz.id)
    
    context = {
        'classes': classes,
    }
    return render(request, 'ecole_app/cours_quiz/creer_quiz.html', context)

@login_required
@user_passes_test(is_professeur_or_admin)
def ajouter_questions(request, quiz_id):
    """Permet à un professeur ou un admin d'ajouter des questions à un quiz"""
    # Vérifier si l'utilisateur est un admin
    is_user_admin = is_admin(request.user) and not hasattr(request.user, 'professeur')
    
    if is_user_admin:
        # Si c'est un admin, il peut modifier n'importe quel quiz
        quiz = get_object_or_404(Quiz, id=quiz_id)
    else:
        # Si c'est un professeur
        professeur = request.user.professeur
        quiz = get_object_or_404(Quiz, id=quiz_id, module__professeur=professeur)
    
    if request.method == 'POST':
        intitule = request.POST.get('intitule')
        type_question = request.POST.get('type_question', 'choix_unique')
        points = request.POST.get('points', 1)
        
        if not intitule:
            messages.error(request, 'L\'intitulé de la question est obligatoire.')
            return redirect('ajouter_questions', quiz_id=quiz.id)
        
        # Vérifier la validité des choix selon le type de question
        if type_question == 'vrai_faux':
            # Pour les questions vrai/faux, vérifier que correct_vf est présent
            correct_vf = request.POST.get('correct_vf')
            if correct_vf not in ['0', '1']:
                messages.error(request, 'Vous devez sélectionner la bonne réponse (Vrai ou Faux).')
                return redirect('ajouter_questions', quiz_id=quiz.id)
        else:
            # Pour les autres types de questions, vérifier qu'il y a au moins deux choix
            choix_textes = request.POST.getlist('choix[]')
            choix_valides = [c for c in choix_textes if c.strip()]
            
            if len(choix_valides) < 2:
                messages.error(request, 'Vous devez spécifier au moins deux choix de réponse.')
                return redirect('ajouter_questions', quiz_id=quiz.id)
            
            # Vérifier qu'au moins une réponse est marquée comme correcte
            choix_corrects = request.POST.getlist('correct[]')
            if not choix_corrects and type_question != 'texte_court':
                messages.error(request, 'Vous devez sélectionner au moins une réponse correcte.')
                return redirect('ajouter_questions', quiz_id=quiz.id)
        
        # Créer la question
        question = Question.objects.create(
            quiz=quiz,
            texte=intitule,
            type=type_question,
            points=points
        )
        
        # Traitement spécial pour les questions vrai/faux
        if type_question == 'vrai_faux':
            # Pour les questions vrai/faux, on utilise les champs spécifiques
            correct_vf = request.POST.get('correct_vf')
            
            # Créer les choix Vrai et Faux
            Choix.objects.create(
                question=question,
                texte='Vrai',
                est_correct=(correct_vf == '0'),
                ordre=0
            )
            
            Choix.objects.create(
                question=question,
                texte='Faux',
                est_correct=(correct_vf == '1'),
                ordre=1
            )
        else:
            # Pour les autres types de questions, traitement normal
            choix_textes = request.POST.getlist('choix[]')
            choix_corrects = request.POST.getlist('correct[]')
            
            for i, choix_texte in enumerate(choix_textes):
                if choix_texte.strip():  # Ignorer les choix vides
                    est_correct = str(i) in choix_corrects
                    Choix.objects.create(
                        question=question,
                        texte=choix_texte,
                        est_correct=est_correct,
                        ordre=i
                    )
        
        messages.success(request, 'La question a été ajoutée avec succès.')
        
        # Rediriger vers la même page pour ajouter d'autres questions
        return redirect('ajouter_questions', quiz_id=quiz.id)
    
    context = {
        'quiz': quiz,
        'questions': quiz.questions.all(),
    }
    return render(request, 'ecole_app/cours_quiz/ajouter_questions.html', context)

@login_required
@user_passes_test(is_professeur_or_admin)
def activer_quiz(request, quiz_id):
    """Permet à un professeur ou un admin d'activer ou désactiver un quiz"""
    # Vérifier si l'utilisateur est un admin
    is_user_admin = is_admin(request.user) and not hasattr(request.user, 'professeur')
    
    if is_user_admin:
        # Si c'est un admin, il peut modifier n'importe quel quiz
        quiz = get_object_or_404(Quiz, id=quiz_id)
    else:
        # Si c'est un professeur
        professeur = request.user.professeur
        quiz = get_object_or_404(Quiz, id=quiz_id, module__professeur=professeur)
    
    quiz.publie = not quiz.publie
    quiz.save()
    
    status = "activé" if quiz.publie else "désactivé"
    messages.success(request, f'Le quiz a été {status} avec succès.')
    
    return redirect('liste_quiz_professeur')

@login_required
def liste_quiz_eleve(request):
    """Affiche la liste des quiz disponibles pour l'élève connecté"""
    eleve = request.user.eleve
    
    # Récupérer les quiz publiés pour les classes de l'élève
    quiz_disponibles = Quiz.objects.filter(
        module__classes__in=eleve.classes.all(),
        publie=True
    ).distinct()
    
    # Récupérer les tentatives de l'élève
    tentatives = TentativeQuiz.objects.filter(eleve=eleve)
    
    # Créer un dictionnaire pour stocker les tentatives par quiz
    tentatives_par_quiz = {}
    for tentative in tentatives:
        tentatives_par_quiz[tentative.quiz.id] = tentative
    
    context = {
        'quiz_disponibles': quiz_disponibles,
        'tentatives_par_quiz': tentatives_par_quiz,
    }
    return render(request, 'ecole_app/cours_quiz/liste_quiz_eleve.html', context)

@login_required
def demarrer_quiz(request, quiz_id):
    """Permet à un élève de démarrer un quiz"""
    eleve = request.user.eleve
    
    # Utiliser filter().first() au lieu de get_object_or_404 pour éviter l'erreur MultipleObjectsReturned
    quiz = Quiz.objects.filter(id=quiz_id, publie=True, module__classes__in=eleve.classes.all()).first()
    
    if not quiz:
        messages.error(request, "Ce quiz n'existe pas ou n'est pas disponible pour votre classe.")
        return redirect('liste_quiz_eleve')
    
    # Vérifier si l'élève a déjà une tentative en cours
    tentative_existante = TentativeQuiz.objects.filter(quiz=quiz, eleve=eleve, terminee=False).first()
    
    if tentative_existante:
        # Continuer la tentative existante
        tentative = tentative_existante
    else:
        # Créer une nouvelle tentative
        tentative = TentativeQuiz.objects.create(
            quiz=quiz,
            eleve=eleve
        )
    
    return redirect('repondre_quiz', tentative_id=tentative.id)

@login_required
def repondre_quiz(request, tentative_id, question_id=None):
    """Permet à l'élève de répondre à une question du quiz"""
    tentative = get_object_or_404(TentativeQuiz, id=tentative_id)
    quiz = tentative.quiz
    
    # Vérifier que l'élève est bien celui qui a commencé la tentative
    if request.user != tentative.eleve.user:
        messages.error(request, "Vous n'êtes pas autorisé à répondre à ce quiz.")
        return redirect('dashboard_eleve')
    
    # Si aucune question n'est spécifiée, prendre la première non répondue
    if question_id is None:
        # Récupérer toutes les questions du quiz
        questions = quiz.questions.all().order_by('ordre')
        
        # Récupérer les questions déjà répondues
        reponses = Reponse.objects.filter(tentative=tentative)
        questions_repondues = [r.question.id for r in reponses]
        
        # Trouver la première question non répondue
        for question in questions:
            if question.id not in questions_repondues:
                return redirect('repondre_quiz', tentative_id=tentative_id, question_id=question.id)
        
        # Si toutes les questions ont été répondues, rediriger vers les résultats
        return redirect('resultats_quiz', tentative_id=tentative_id)
    
    # Récupérer la question courante
    question_courante = get_object_or_404(Question, id=question_id, quiz=quiz)
    
    # Vérifier si la question a déjà été répondue
    if Reponse.objects.filter(tentative=tentative, question=question_courante).exists():
        messages.warning(request, "Vous avez déjà répondu à cette question.")
        return redirect('repondre_quiz', tentative_id=tentative_id)
    
    if request.method == 'POST':
        # Traiter la réponse
        if question_courante.type == 'texte_court':
            texte_reponse = request.POST.get('texte_reponse', '').strip()
            if not texte_reponse:
                messages.error(request, "Veuillez entrer une réponse.")
                return render(request, 'ecole_app/cours_quiz/repondre_quiz.html', {
                    'tentative': tentative,
                    'question': question_courante,
                    'choix': question_courante.choix.all(),
                })
            
            # Créer la réponse
            reponse = Reponse(
                tentative=tentative,
                question=question_courante,
                texte_reponse=texte_reponse,
                est_correcte=False  # À implémenter: vérification des réponses textuelles
            )
            reponse.save()
        else:
            # Pour les questions à choix
            choix_ids = request.POST.getlist('choix')
            if not choix_ids:
                messages.error(request, "Veuillez sélectionner au moins une réponse.")
                return render(request, 'ecole_app/cours_quiz/repondre_quiz.html', {
                    'tentative': tentative,
                    'question': question_courante,
                    'choix': question_courante.choix.all(),
                })
            
            # Utiliser une transaction pour garantir la cohérence
            with transaction.atomic():
                try:
                    # Créer et sauvegarder d'abord la réponse pour qu'elle ait un ID
                    reponse = Reponse(
                        tentative=tentative,
                        question=question_courante,
                        est_correcte=False
                    )
                    reponse.save()
                    
                    # Ajouter les choix un par un après avoir sauvegardé la réponse
                    for choix_id in choix_ids:
                        choix = get_object_or_404(Choix, id=choix_id, question=question_courante)
                        reponse.choix_selectionnes.add(choix)
                    
                    # Rafraîchir l'objet depuis la base de données
                    reponse.refresh_from_db()
                    
                    # Mettre à jour le statut de la réponse
                    est_correcte = reponse.verifier_reponse()
                    Reponse.objects.filter(pk=reponse.pk).update(est_correcte=est_correcte)
                except Exception as e:
                    # Journaliser l'erreur pour le débogage
                    print(f"Erreur lors de la création de la réponse: {e}")
                    messages.error(request, "Une erreur s'est produite lors de l'enregistrement de votre réponse. Veuillez réessayer.")
                    return render(request, 'ecole_app/cours_quiz/repondre_quiz.html', {
                        'tentative': tentative,
                        'question': question_courante,
                        'choix': question_courante.choix.all(),
                    })
        
        # Passer à la question suivante ou terminer le quiz
        questions = quiz.questions.all().order_by('ordre')
        questions_repondues = [r.question.id for r in Reponse.objects.filter(tentative=tentative)]
        
        for question in questions:
            if question.id not in questions_repondues:
                return redirect('repondre_quiz', tentative_id=tentative_id, question_id=question.id)
        
        # Toutes les questions ont été répondues
        return redirect('resultats_quiz', tentative_id=tentative_id)
    
    # Récupérer les questions déjà répondues
    questions = quiz.questions.all().order_by('ordre')
    questions_repondues = [r.question.id for r in Reponse.objects.filter(tentative=tentative)]
    total_questions = questions.count()
    
    # Calculer la progression en pourcentage
    if total_questions > 0:
        # Inclure la question courante dans le calcul de la progression
        questions_completees = len(questions_repondues)
        progression_percent = (questions_completees * 100) // total_questions
    else:
        progression_percent = 0
    
    context = {
        'tentative': tentative,
        'question': question_courante,
        'choix': question_courante.choix.all() if question_courante else None,
        'progression': len(questions_repondues) + 1,  # Numéro de la question actuelle
        'progression_percent': progression_percent,  # Pourcentage de progression
        'total_questions': total_questions,
    }
    return render(request, 'ecole_app/cours_quiz/repondre_quiz.html', context)

@login_required
def terminer_quiz(request, tentative_id):
    """Termine un quiz et calcule le score"""
    eleve = request.user.eleve
    tentative = get_object_or_404(TentativeQuiz, id=tentative_id, eleve=eleve)
    
    # Si la tentative est déjà terminée, rediriger vers les résultats
    if tentative.terminee:
        return redirect('resultats_quiz', tentative_id=tentative.id)
    
    # Calculer le score
    total_points = sum(q.points for q in tentative.quiz.questions.all())
    points_obtenus = 0
    
    for reponse_eleve in tentative.reponses.all():
        if reponse_eleve.est_correcte:
            points_obtenus += reponse_eleve.question.points
    
    # Calculer le score en pourcentage
    if total_points > 0:
        score = (points_obtenus / total_points) * 100
    else:
        score = 0
    
    # Mettre à jour la tentative
    tentative.score = score
    tentative.date_fin = timezone.now()
    tentative.terminee = True
    tentative.save()
    
    return redirect('resultats_quiz', tentative_id=tentative.id)

@login_required
def resultats_quiz(request, tentative_id):
    """Affiche les résultats d'un quiz"""
    eleve = request.user.eleve
    tentative = get_object_or_404(TentativeQuiz, id=tentative_id, eleve=eleve)
    
    # S'assurer que la tentative est marquée comme terminée
    if not tentative.terminee:
        # Calculer le score
        total_points = sum(q.points for q in tentative.quiz.questions.all())
        points_obtenus = 0
        
        for reponse_eleve in tentative.reponses.all():
            if reponse_eleve.est_correcte:
                points_obtenus += reponse_eleve.question.points
        
        # Calculer le score en pourcentage
        if total_points > 0:
            score = (points_obtenus / total_points) * 100
        else:
            score = 0
        
        # Mettre à jour la tentative
        tentative.score = score
        tentative.date_fin = timezone.now()
        tentative.terminee = True
        tentative.save()
    
    # Récupérer les réponses de l'élève avec les questions et les réponses correctes
    reponses_eleve = tentative.reponses.all().select_related('question')
    
    # Préparer les données pour l'affichage
    resultats_detailles = []
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
        resultats_detailles.append(resultat)
    
    context = {
        'tentative': tentative,
        'resultats_detailles': resultats_detailles,
    }
    return render(request, 'ecole_app/cours_quiz/resultats_quiz.html', context)

@login_required
@user_passes_test(is_professeur_or_admin)
def resultats_quiz_classe(request, quiz_id):
    """Affiche les résultats d'un quiz pour une classe"""
    # Vérifier si l'utilisateur est un admin
    is_user_admin = is_admin(request.user) and not hasattr(request.user, 'professeur')
    
    if is_user_admin:
        # Si c'est un admin, il peut voir les résultats de n'importe quel quiz
        quiz = get_object_or_404(Quiz, id=quiz_id)
    else:
        # Si c'est un professeur
        professeur = request.user.professeur
        quiz = get_object_or_404(Quiz, id=quiz_id, module__professeur=professeur)
    
    # Récupérer toutes les tentatives pour ce quiz
    tentatives = TentativeQuiz.objects.filter(quiz=quiz, terminee=True).order_by('-score')
    
    context = {
        'quiz': quiz,
        'tentatives': tentatives,
    }
    return render(request, 'ecole_app/cours_quiz/resultats_quiz_classe.html', context)

@login_required
@user_passes_test(is_professeur_or_admin)
def supprimer_quiz(request, quiz_id):
    """Permet à un professeur ou un admin de supprimer un quiz"""
    # Vérifier si l'utilisateur est un admin
    is_user_admin = is_admin(request.user) and not hasattr(request.user, 'professeur')
    
    if is_user_admin:
        # Si c'est un admin, il peut supprimer n'importe quel quiz
        quiz = get_object_or_404(Quiz, id=quiz_id)
    else:
        # Si c'est un professeur
        professeur = request.user.professeur
        quiz = get_object_or_404(Quiz, id=quiz_id, module__professeur=professeur)
    
    if request.method == 'POST':
        # Supprimer le module associé au quiz (ce qui supprimera aussi le quiz par cascade)
        module = quiz.module
        module.delete()
        messages.success(request, 'Le quiz a été supprimé avec succès.')
        return redirect('liste_quiz_professeur')
    
    context = {
        'quiz': quiz,
    }
    return render(request, 'ecole_app/cours_quiz/supprimer_quiz.html', context)
