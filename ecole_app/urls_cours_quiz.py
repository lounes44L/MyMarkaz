from django.urls import path, re_path
from . import views_cours_quiz, views_pdf

urlpatterns = [
    # URLs pour les cours partagés - Professeur
    path('cours/professeur/', views_cours_quiz.liste_cours_professeur, name='liste_cours_professeur'),
    path('cours/ajouter/', views_cours_quiz.ajouter_cours, name='ajouter_cours'),
    path('cours/<int:cours_id>/modifier/', views_cours_quiz.modifier_cours, name='modifier_cours'),
    path('cours/<int:cours_id>/supprimer/', views_cours_quiz.supprimer_cours, name='supprimer_cours'),
    
    # URLs pour les cours partagés - Élève
    path('cours/eleve/', views_cours_quiz.liste_cours_eleve, name='liste_cours_eleve'),
    path('cours/<int:cours_id>/telecharger/', views_cours_quiz.telecharger_cours, name='telecharger_cours'),
    
    # URLs pour les quiz - Professeur
    path('quiz/professeur/', views_cours_quiz.liste_quiz_professeur, name='liste_quiz_professeur'),
    path('quiz/creer/', views_cours_quiz.creer_quiz, name='creer_quiz'),
    path('quiz/<int:quiz_id>/questions/', views_cours_quiz.ajouter_questions, name='ajouter_questions'),
    path('quiz/<int:quiz_id>/activer/', views_cours_quiz.activer_quiz, name='activer_quiz'),
    path('quiz/<int:quiz_id>/resultats/', views_cours_quiz.resultats_quiz_classe, name='resultats_quiz_classe'),
    path('quiz/<int:quiz_id>/supprimer/', views_cours_quiz.supprimer_quiz, name='supprimer_quiz'),
    
    # URLs pour les quiz - Élève
    path('quiz/eleve/', views_cours_quiz.liste_quiz_eleve, name='liste_quiz_eleve'),
    path('quiz/<int:quiz_id>/demarrer/', views_cours_quiz.demarrer_quiz, name='demarrer_quiz'),
    # Utiliser un seul chemin avec un paramètre optionnel pour question_id
    re_path(r'^quiz/repondre/(?P<tentative_id>[0-9]+)(?:/(?P<question_id>[0-9]+))?/$', views_cours_quiz.repondre_quiz, name='repondre_quiz'),
    path('quiz/resultats/<int:tentative_id>/', views_cours_quiz.resultats_quiz, name='resultats_quiz'),
    path('quiz/resultats/<int:tentative_id>/pdf/', views_pdf.telecharger_resultats_quiz_pdf, name='telecharger_resultats_quiz_pdf'),
]
