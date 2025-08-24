from django.core.management.base import BaseCommand
from ecole_app.models import CompetenceLivre

class Command(BaseCommand):
    help = 'Initialise les compétences du livre pour la leçon 8'

    def handle(self, *args, **options):
        # Supprimer les compétences existantes pour la leçon 8
        CompetenceLivre.objects.filter(lecon=8).delete()
        
        # Créer les compétences pour la leçon 8
        competences = [
            # Leçon 8
            {
                'lecon': 8,
                'description': 'Capacité à reconnaître et prononcer les lettres avec chadda ;',
                'ordre': 1
            },
            {
                'lecon': 8,
                'description': 'Capacité à identifier la différence entre une lettre avec chadda et sans chadda ;',
                'ordre': 2
            },
            {
                'lecon': 8,
                'description': 'Compétences générales en prononciation des mots avec chadda ;',
                'ordre': 3
            },
            {
                'lecon': 8,
                'description': 'Capacité à lire fluidement le texte, les exemples et l\'exercice 10.',
                'ordre': 4
            },
            {
                'lecon': 8,
                'description': 'Capacité à appliquer correctement les règles de prononciation de la chadda.',
                'ordre': 5
            },
        ]
        
        # Créer les compétences
        for comp_data in competences:
            CompetenceLivre.objects.create(**comp_data)
            
        self.stdout.write(self.style.SUCCESS(f'Compétences de la leçon 8 créées avec succès : {len(competences)}'))
