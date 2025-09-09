from django.urls import path
from . import views_pedagogie

urlpatterns = [
    # URLs pour les professeurs
    path('modules/', views_pedagogie.liste_modules, name='liste_modules'),
    path('modules/creer/', views_pedagogie.creer_module, name='creer_module'),
    path('modules/<int:module_id>/', views_pedagogie.detail_module, name='detail_module'),
    path('modules/<int:module_id>/modifier/', views_pedagogie.modifier_module, name='modifier_module'),
    path('modules/<int:module_id>/ajouter-document/', views_pedagogie.ajouter_document, name='ajouter_document'),
    path('modules/<int:module_id>/creer-quiz/', views_pedagogie.creer_quiz, name='creer_quiz'),
    path('quiz/<int:quiz_id>/editer/', views_pedagogie.editer_quiz, name='editer_quiz'),
    path('quiz/<int:quiz_id>/ajouter-question/', views_pedagogie.ajouter_question, name='ajouter_question'),
    path('quiz/<int:quiz_id>/statistiques/', views_pedagogie.statistiques_quiz, name='statistiques_quiz'),
    
    # URLs pour les élèves
    path('mes-modules/', views_pedagogie.modules_eleve, name='modules_eleve'),
    path('mes-modules/<int:module_id>/', views_pedagogie.module_eleve_detail, name='module_eleve_detail'),
    path('quiz/<int:quiz_id>/demarrer/', views_pedagogie.demarrer_quiz, name='demarrer_quiz'),
    path('quiz/tentative/<int:tentative_id>/', views_pedagogie.repondre_quiz, name='repondre_quiz'),
    path('quiz/resultat/<int:tentative_id>/', views_pedagogie.resultat_quiz, name='resultat_quiz'),
]
