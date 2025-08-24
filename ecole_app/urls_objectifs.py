from django.urls import path
from . import views_objectifs

urlpatterns = [
    path('ajouter-objectif/', views_objectifs.ajouter_objectif, name='ajouter_objectif'),
    path('modifier-statut-objectif/<int:objectif_id>/<str:statut>/', views_objectifs.modifier_statut_objectif, name='modifier_statut_objectif'),
]
