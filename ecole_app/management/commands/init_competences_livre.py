from django.core.management.base import BaseCommand
from ecole_app.models import CompetenceLivre

class Command(BaseCommand):
    help = 'Initialise les compétences du livre pour les leçons 1 et 2'

    def handle(self, *args, **options):
        # Supprimer les compétences existantes pour les leçons 1 et 2
        CompetenceLivre.objects.filter(lecon__in=[1, 2]).delete()
        
        # Créer les compétences pour les leçons 1 et 2
        competences = [
            # Leçon 1 et 2
            {
                'lecon': 1,
                'description': 'Capacité à reconnaître et lire les lettres fortes ;',
                'ordre': 1
            },
            {
                'lecon': 1,
                'description': 'Capacité à identifier la position des lettres dans un mot ;',
                'ordre': 2
            },
            {
                'lecon': 1,
                'description': 'Capacité à identifier et lire les lettres qui nécessitent de tirer le bout de la langue ;',
                'ordre': 3
            },
            {
                'lecon': 1,
                'description': 'Capacité à lire les lettres mises dans le désordre ;',
                'ordre': 4
            },
            {
                'lecon': 1,
                'description': 'Compétences générales en prononciation.',
                'ordre': 5
            },
        ]
        
        # Créer les compétences
        for comp_data in competences:
            CompetenceLivre.objects.create(**comp_data)
            
        self.stdout.write(self.style.SUCCESS(f'Compétences créées avec succès : {len(competences)}'))
