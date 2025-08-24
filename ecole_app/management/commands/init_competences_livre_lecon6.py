from django.core.management.base import BaseCommand
from ecole_app.models import CompetenceLivre

class Command(BaseCommand):
    help = 'Initialise les compétences du livre pour la leçon 6'

    def handle(self, *args, **options):
        # Supprimer les compétences existantes pour la leçon 6
        CompetenceLivre.objects.filter(lecon=6).delete()
        
        # Créer les compétences pour la leçon 6
        competences = [
            # Leçon 6
            {
                'lecon': 6,
                'description': 'Capacité à reconnaître les lettres de prolongement ;',
                'ordre': 1
            },
            {
                'lecon': 6,
                'description': 'Capacité à distinguer les voyelles courtes des voyelles longues ;',
                'ordre': 2
            },
            {
                'lecon': 6,
                'description': 'Capacité à distinguer les lettres de line des lettres de prolongement ;',
                'ordre': 3
            },
            {
                'lecon': 6,
                'description': 'Compétences générales en prononciation ;',
                'ordre': 4
            },
            {
                'lecon': 6,
                'description': 'Capacité à lire fluidement le texte, les exemples et l\'exercice 8.',
                'ordre': 5
            },
        ]
        
        # Créer les compétences
        for comp_data in competences:
            CompetenceLivre.objects.create(**comp_data)
            
        self.stdout.write(self.style.SUCCESS(f'Compétences de la leçon 6 créées avec succès : {len(competences)}'))
