from django.core.management.base import BaseCommand
from ecole_app.models import CompetenceLivre

class Command(BaseCommand):
    help = 'Initialise les compétences du livre pour la leçon 7'

    def handle(self, *args, **options):
        # Supprimer les compétences existantes pour la leçon 7
        CompetenceLivre.objects.filter(lecon=7).delete()
        
        # Créer les compétences pour la leçon 7
        competences = [
            # Leçon 7
            {
                'lecon': 7,
                'description': 'Capacité à identifier les différents types de doubles voyelles ;',
                'ordre': 1
            },
            {
                'lecon': 7,
                'description': 'Capacité à maîtriser l\'arrêt sur les doubles voyelles ;',
                'ordre': 2
            },
            {
                'lecon': 7,
                'description': 'Compétences générales en prononciation ;',
                'ordre': 3
            },
            {
                'lecon': 7,
                'description': 'Capacité à lire fluidement le texte, les exemples et l\'exercice 9.',
                'ordre': 4
            },
            {
                'lecon': 7,
                'description': 'Capacité à distinguer la particularité des doubles voyelles fathatayn par rapport aux autres doubles voyelles.',
                'ordre': 5
            },
        ]
        
        # Créer les compétences
        for comp_data in competences:
            CompetenceLivre.objects.create(**comp_data)
            
        self.stdout.write(self.style.SUCCESS(f'Compétences de la leçon 7 créées avec succès : {len(competences)}'))
