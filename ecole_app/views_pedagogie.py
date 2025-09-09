from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Avg, Sum
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied

from .models import Professeur, Eleve, Classe
from .models_pedagogie import (
    Module, Document, Quiz, Question, Choix, 
    TentativeQuiz, Reponse
)

import json
import os

# Vues pour les professeurs

@login_required
def liste_modules(request):
    """Affiche la liste des modules créés par le professeur connecté"""
    # Vérifier si l'utilisateur est un professeur
    try:
        professeur = request.user.professeur
    except:
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('dashboard')
    
    # Récupérer tous les modules du professeur
    modules = Module.objects.filter(professeur=professeur).order_by('-date_creation')
    
    # Ajouter des statistiques pour chaque module
    for module in modules:
        module.nb_documents = module.documents.count()
        module.nb_quiz = module.quiz.count()
        module.nb_classes = module.classes.count()
    
    context = {
        'modules': modules,
    }
    
    return render(request, 'ecole_app/pedagogie/liste_modules.html', context)

@login_required
def creer_module(request):
    """Permet au professeur de créer un nouveau module"""
    # Vérifier si l'utilisateur est un professeur
    try:
        professeur = request.user.professeur
    except:
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        titre = request.POST.get('titre')
        description = request.POST.get('description')
        classes_ids = request.POST.getlist('classes')
        publie = request.POST.get('publie') == 'on'
        
        if not titre:
            messages.error(request, "Le titre est obligatoire.")
            return redirect('creer_module')
        
        # Créer le module
        module = Module.objects.create(
            titre=titre,
            description=description,
            professeur=professeur,
            publie=publie
        )
        
        # Ajouter les classes sélectionnées
        if classes_ids:
            classes = Classe.objects.filter(id__in=classes_ids)
            module.classes.set(classes)
        
        messages.success(request, f"Le module '{titre}' a été créé avec succès.")
        return redirect('detail_module', module_id=module.id)
    
    # Récupérer les classes du professeur
    classes = Classe.objects.filter(professeur=professeur)
    
    context = {
        'classes': classes,
    }
    
    return render(request, 'ecole_app/pedagogie/creer_module.html', context)

@login_required
def detail_module(request, module_id):
    """Affiche les détails d'un module et permet de le modifier"""
    # Vérifier si l'utilisateur est un professeur
    try:
        professeur = request.user.professeur
    except:
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('dashboard')
    
    # Récupérer le module
    module = get_object_or_404(Module, id=module_id)
    
    # Vérifier que le module appartient au professeur
    if module.professeur != professeur:
        messages.error(request, "Vous n'avez pas accès à ce module.")
        return redirect('liste_modules')
    
    # Récupérer les documents et quiz du module
    documents = module.documents.all().order_by('ordre', 'date_creation')
    quiz = module.quiz.all().order_by('ordre', 'date_creation')
    
    # Récupérer les classes du professeur pour le formulaire de modification
    classes = Classe.objects.filter(professeur=professeur)
    
    context = {
        'module': module,
        'documents': documents,
        'quiz': quiz,
        'classes': classes,
    }
    
    return render(request, 'ecole_app/pedagogie/detail_module.html', context)

@login_required
def modifier_module(request, module_id):
    """Permet au professeur de modifier un module existant"""
    # Vérifier si l'utilisateur est un professeur
    try:
        professeur = request.user.professeur
    except:
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('dashboard')
    
    # Récupérer le module
    module = get_object_or_404(Module, id=module_id)
    
    # Vérifier que le module appartient au professeur
    if module.professeur != professeur:
        messages.error(request, "Vous n'avez pas accès à ce module.")
        return redirect('liste_modules')
    
    if request.method == 'POST':
        titre = request.POST.get('titre')
        description = request.POST.get('description')
        classes_ids = request.POST.getlist('classes')
        publie = request.POST.get('publie') == 'on'
        
        if not titre:
            messages.error(request, "Le titre est obligatoire.")
            return redirect('modifier_module', module_id=module.id)
        
        # Mettre à jour le module
        module.titre = titre
        module.description = description
        module.publie = publie
        module.save()
        
        # Mettre à jour les classes
        if classes_ids:
            classes = Classe.objects.filter(id__in=classes_ids)
            module.classes.set(classes)
        else:
            module.classes.clear()
        
        messages.success(request, f"Le module '{titre}' a été modifié avec succès.")
        return redirect('detail_module', module_id=module.id)
    
    # Récupérer les classes du professeur
    classes = Classe.objects.filter(professeur=professeur)
    
    context = {
        'module': module,
        'classes': classes,
    }
    
    return render(request, 'ecole_app/pedagogie/modifier_module.html', context)

@login_required
def ajouter_document(request, module_id):
    """Permet au professeur d'ajouter un document à un module"""
    # Vérifier si l'utilisateur est un professeur
    try:
        professeur = request.user.professeur
    except:
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('dashboard')
    
    # Récupérer le module
    module = get_object_or_404(Module, id=module_id)
    
    # Vérifier que le module appartient au professeur
    if module.professeur != professeur:
        messages.error(request, "Vous n'avez pas accès à ce module.")
        return redirect('liste_modules')
    
    if request.method == 'POST':
        titre = request.POST.get('titre')
        description = request.POST.get('description')
        fichier = request.FILES.get('fichier')
        ordre = request.POST.get('ordre', 0)
        
        if not titre or not fichier:
            messages.error(request, "Le titre et le fichier sont obligatoires.")
            return redirect('ajouter_document', module_id=module.id)
        
        # Vérifier que le fichier est un PDF
        if not fichier.name.endswith('.pdf'):
            messages.error(request, "Le fichier doit être au format PDF.")
            return redirect('ajouter_document', module_id=module.id)
        
        # Créer le document
        document = Document.objects.create(
            module=module,
            titre=titre,
            description=description,
            fichier=fichier,
            ordre=ordre
        )
        
        messages.success(request, f"Le document '{titre}' a été ajouté avec succès.")
        return redirect('detail_module', module_id=module.id)
    
    context = {
        'module': module,
    }
    
    return render(request, 'ecole_app/pedagogie/ajouter_document.html', context)

@login_required
def creer_quiz(request, module_id):
    """Permet au professeur de créer un quiz pour un module"""
    # Vérifier si l'utilisateur est un professeur
    try:
        professeur = request.user.professeur
    except:
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('dashboard')
    
    # Récupérer le module
    module = get_object_or_404(Module, id=module_id)
    
    # Vérifier que le module appartient au professeur
    if module.professeur != professeur:
        messages.error(request, "Vous n'avez pas accès à ce module.")
        return redirect('liste_modules')
    
    if request.method == 'POST':
        titre = request.POST.get('titre')
        description = request.POST.get('description')
        temps_limite = request.POST.get('temps_limite')
        publie = request.POST.get('publie') == 'on'
        ordre = request.POST.get('ordre', 0)
        
        if not titre:
            messages.error(request, "Le titre est obligatoire.")
            return redirect('creer_quiz', module_id=module.id)
        
        # Créer le quiz
        quiz = Quiz.objects.create(
            module=module,
            titre=titre,
            description=description,
            temps_limite=temps_limite if temps_limite else None,
            publie=publie,
            ordre=ordre
        )
        
        messages.success(request, f"Le quiz '{titre}' a été créé avec succès.")
        return redirect('editer_quiz', quiz_id=quiz.id)
    
    context = {
        'module': module,
    }
    
    return render(request, 'ecole_app/pedagogie/creer_quiz.html', context)

@login_required
def editer_quiz(request, quiz_id):
    """Permet au professeur d'éditer un quiz existant"""
    # Vérifier si l'utilisateur est un professeur
    try:
        professeur = request.user.professeur
    except:
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('dashboard')
    
    # Récupérer le quiz
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Vérifier que le quiz appartient au professeur
    if quiz.module.professeur != professeur:
        messages.error(request, "Vous n'avez pas accès à ce quiz.")
        return redirect('liste_modules')
    
    # Récupérer les questions du quiz
    questions = quiz.questions.all().order_by('ordre')
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'types_questions': Question.TYPES,
    }
    
    return render(request, 'ecole_app/pedagogie/editer_quiz.html', context)

@login_required
@require_POST
def ajouter_question(request, quiz_id):
    """Ajoute une question à un quiz (AJAX)"""
    # Vérifier si l'utilisateur est un professeur
    try:
        professeur = request.user.professeur
    except:
        return JsonResponse({'success': False, 'message': "Vous n'avez pas accès à cette page."})
    
    # Récupérer le quiz
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Vérifier que le quiz appartient au professeur
    if quiz.module.professeur != professeur:
        return JsonResponse({'success': False, 'message': "Vous n'avez pas accès à ce quiz."})
    
    # Récupérer les données de la question
    data = json.loads(request.body)
    texte = data.get('texte')
    type_question = data.get('type')
    points = data.get('points', 1)
    ordre = data.get('ordre', 0)
    choix = data.get('choix', [])
    
    if not texte or not type_question:
        return JsonResponse({'success': False, 'message': "Le texte et le type de question sont obligatoires."})
    
    # Créer la question
    question = Question.objects.create(
        quiz=quiz,
        texte=texte,
        type=type_question,
        points=points,
        ordre=ordre
    )
    
    # Ajouter les choix si nécessaire
    if type_question in ['choix_unique', 'choix_multiple', 'vrai_faux']:
        for choix_data in choix:
            Choix.objects.create(
                question=question,
                texte=choix_data['texte'],
                est_correct=choix_data['est_correct'],
                ordre=choix_data['ordre']
            )
    
    return JsonResponse({
        'success': True, 
        'message': "Question ajoutée avec succès.",
        'question_id': question.id
    })

# Vues pour les élèves

@login_required
def modules_eleve(request):
    """Affiche la liste des modules disponibles pour l'élève connecté"""
    # Vérifier si l'utilisateur est un élève
    try:
        eleve = request.user.eleve
    except:
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('dashboard')
    
    # Récupérer les modules disponibles pour l'élève (via sa classe)
    modules = Module.objects.filter(
        classes=eleve.classe,
        publie=True
    ).distinct().order_by('-date_creation')
    
    context = {
        'modules': modules,
    }
    
    return render(request, 'ecole_app/pedagogie/modules_eleve.html', context)

@login_required
def module_eleve_detail(request, module_id):
    """Affiche le détail d'un module pour un élève"""
    # Vérifier si l'utilisateur est un élève
    try:
        eleve = request.user.eleve
    except:
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('dashboard')
    
    # Récupérer le module
    module = get_object_or_404(Module, id=module_id, publie=True)
    
    # Vérifier que l'élève a accès à ce module
    if eleve.classe not in module.classes.all():
        messages.error(request, "Vous n'avez pas accès à ce module.")
        return redirect('modules_eleve')
    
    # Récupérer les documents et quiz du module
    documents = module.documents.all().order_by('ordre', 'date_creation')
    quiz_list = module.quiz.filter(publie=True).order_by('ordre', 'date_creation')
    
    # Pour chaque quiz, vérifier si l'élève l'a déjà complété
    for quiz in quiz_list:
        tentatives = TentativeQuiz.objects.filter(quiz=quiz, eleve=eleve, terminee=True)
        quiz.tentatives = tentatives
        quiz.meilleur_score = tentatives.order_by('-score').first().score if tentatives.exists() else None
    
    context = {
        'module': module,
        'documents': documents,
        'quiz_list': quiz_list,
    }
    
    return render(request, 'ecole_app/pedagogie/module_eleve_detail.html', context)

@login_required
def demarrer_quiz(request, quiz_id):
    """Permet à un élève de démarrer un quiz"""
    # Vérifier si l'utilisateur est un élève
    try:
        eleve = request.user.eleve
    except:
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('dashboard')
    
    # Récupérer le quiz
    quiz = get_object_or_404(Quiz, id=quiz_id, publie=True)
    
    # Vérifier que l'élève a accès à ce quiz
    if eleve.classe not in quiz.module.classes.all():
        messages.error(request, "Vous n'avez pas accès à ce quiz.")
        return redirect('modules_eleve')
    
    # Créer une nouvelle tentative
    tentative = TentativeQuiz.objects.create(
        quiz=quiz,
        eleve=eleve
    )
    
    return redirect('repondre_quiz', tentative_id=tentative.id)

@login_required
def repondre_quiz(request, tentative_id):
    """Permet à un élève de répondre à un quiz"""
    # Vérifier si l'utilisateur est un élève
    try:
        eleve = request.user.eleve
    except:
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('dashboard')
    
    # Récupérer la tentative
    tentative = get_object_or_404(TentativeQuiz, id=tentative_id)
    
    # Vérifier que la tentative appartient à l'élève
    if tentative.eleve != eleve:
        messages.error(request, "Vous n'avez pas accès à cette tentative.")
        return redirect('modules_eleve')
    
    # Vérifier que la tentative n'est pas déjà terminée
    if tentative.terminee:
        return redirect('resultat_quiz', tentative_id=tentative.id)
    
    # Récupérer le quiz et ses questions
    quiz = tentative.quiz
    questions = quiz.questions.all().order_by('ordre')
    
    if request.method == 'POST':
        # Traiter les réponses
        for question in questions:
            if question.type == 'choix_unique' or question.type == 'vrai_faux':
                choix_id = request.POST.get(f'question_{question.id}')
                if choix_id:
                    choix = get_object_or_404(Choix, id=choix_id)
                    reponse = Reponse.objects.create(
                        tentative=tentative,
                        question=question
                    )
                    reponse.choix_selectionnes.add(choix)
                    reponse.est_correcte = choix.est_correct
                    reponse.save()
            
            elif question.type == 'choix_multiple':
                choix_ids = request.POST.getlist(f'question_{question.id}')
                if choix_ids:
                    reponse = Reponse.objects.create(
                        tentative=tentative,
                        question=question
                    )
                    choix_selectionnes = Choix.objects.filter(id__in=choix_ids)
                    reponse.choix_selectionnes.set(choix_selectionnes)
                    
                    # Vérifier si tous les choix corrects sont sélectionnés et aucun incorrect
                    choix_corrects = question.choix.filter(est_correct=True)
                    if (choix_corrects.count() == choix_selectionnes.filter(est_correct=True).count() and
                            not choix_selectionnes.filter(est_correct=False).exists()):
                        reponse.est_correcte = True
                    else:
                        reponse.est_correcte = False
                    reponse.save()
            
            elif question.type == 'texte_court':
                texte_reponse = request.POST.get(f'question_{question.id}')
                if texte_reponse:
                    reponse = Reponse.objects.create(
                        tentative=tentative,
                        question=question,
                        texte_reponse=texte_reponse
                    )
                    # Pour les réponses textuelles, la vérification est plus complexe
                    # On pourrait implémenter une comparaison avec des réponses attendues
                    reponse.est_correcte = False  # Par défaut
                    reponse.save()
        
        # Calculer le score
        total_points = sum(q.points for q in questions)
        if total_points > 0:
            points_obtenus = sum(r.question.points for r in tentative.reponses.filter(est_correcte=True))
            score = (points_obtenus / total_points) * 100
        else:
            score = 0
        
        # Marquer la tentative comme terminée
        tentative.terminee = True
        tentative.date_fin = timezone.now()
        tentative.score = score
        tentative.save()
        
        return redirect('resultat_quiz', tentative_id=tentative.id)
    
    context = {
        'tentative': tentative,
        'quiz': quiz,
        'questions': questions,
    }
    
    return render(request, 'ecole_app/pedagogie/repondre_quiz.html', context)

@login_required
def resultat_quiz(request, tentative_id):
    """Affiche les résultats d'un quiz pour un élève"""
    # Vérifier si l'utilisateur est un élève
    try:
        eleve = request.user.eleve
    except:
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('dashboard')
    
    # Récupérer la tentative
    tentative = get_object_or_404(TentativeQuiz, id=tentative_id, terminee=True)
    
    # Vérifier que la tentative appartient à l'élève
    if tentative.eleve != eleve:
        messages.error(request, "Vous n'avez pas accès à cette tentative.")
        return redirect('modules_eleve')
    
    # Récupérer les réponses
    reponses = tentative.reponses.all()
    
    context = {
        'tentative': tentative,
        'quiz': tentative.quiz,
        'reponses': reponses,
    }
    
    return render(request, 'ecole_app/pedagogie/resultat_quiz.html', context)

# Vues pour les statistiques (professeurs)

@login_required
def statistiques_quiz(request, quiz_id):
    """Affiche les statistiques d'un quiz pour un professeur"""
    # Vérifier si l'utilisateur est un professeur
    try:
        professeur = request.user.professeur
    except:
        messages.error(request, "Vous n'avez pas accès à cette page.")
        return redirect('dashboard')
    
    # Récupérer le quiz
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Vérifier que le quiz appartient au professeur
    if quiz.module.professeur != professeur:
        messages.error(request, "Vous n'avez pas accès à ce quiz.")
        return redirect('liste_modules')
    
    # Récupérer les tentatives terminées
    tentatives = TentativeQuiz.objects.filter(quiz=quiz, terminee=True)
    
    # Calculer les statistiques
    nb_tentatives = tentatives.count()
    score_moyen = tentatives.aggregate(Avg('score'))['score__avg'] or 0
    
    # Statistiques par question
    questions = quiz.questions.all()
    stats_questions = []
    
    for question in questions:
        reponses = Reponse.objects.filter(question=question, tentative__in=tentatives)
        nb_reponses = reponses.count()
        nb_correctes = reponses.filter(est_correcte=True).count()
        taux_reussite = (nb_correctes / nb_reponses * 100) if nb_reponses > 0 else 0
        
        stats_questions.append({
            'question': question,
            'nb_reponses': nb_reponses,
            'nb_correctes': nb_correctes,
            'taux_reussite': taux_reussite,
        })
    
    # Statistiques par élève
    stats_eleves = []
    
    for tentative in tentatives:
        stats_eleves.append({
            'eleve': tentative.eleve,
            'date': tentative.date_fin,
            'score': tentative.score,
        })
    
    context = {
        'quiz': quiz,
        'nb_tentatives': nb_tentatives,
        'score_moyen': score_moyen,
        'stats_questions': stats_questions,
        'stats_eleves': stats_eleves,
    }
    
    return render(request, 'ecole_app/pedagogie/statistiques_quiz.html', context)
