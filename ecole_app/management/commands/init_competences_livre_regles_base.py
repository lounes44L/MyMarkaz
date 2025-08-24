from django.core.management.base import BaseCommand
from ecole_app.models import CompetenceLivre

class Command(BaseCommand):
    help = 'Initialise les compétences du livre pour les règles de base'

    def handle(self, *args, **options):
        # Supprimer les compétences existantes pour les règles de base
        CompetenceLivre.objects.filter(lecon=0).delete()
        
        # Créer les compétences pour les règles de base
        competences = [
            # Règles de base
            {
                'lecon': 0,
                'description': 'Capacité à appliquer la nasalisation (الغُنَّة) sur le noun ;',
                'ordre': 1
            },
            {
                'lecon': 0,
                'description': 'Maîtrise des différentes déclinaisons de ن ;',
                'ordre': 2
            },
            {
                'lecon': 0,
                'description': 'Capacité à distinguer les différents types de prolongement plus de 2 temps ;',
                'ordre': 3
            },
            {
                'lecon': 0,
                'description': 'Maîtrise les types de القَلْقَلَة.',
                'ordre': 4
            },
        ]
        
        # Créer les compétences
        for comp_data in competences:
            CompetenceLivre.objects.create(**comp_data)
            
        self.stdout.write(self.style.SUCCESS(f'Compétences des règles de base créées avec succès : {len(competences)}'))
