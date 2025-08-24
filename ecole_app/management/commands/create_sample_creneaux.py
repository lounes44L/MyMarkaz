from django.core.management.base import BaseCommand
from ecole_app.models import Creneau

class Command(BaseCommand):
    help = 'Crée quelques créneaux de test si aucun n\'existe.'

    def handle(self, *args, **options):
        if Creneau.objects.exists():
            self.stdout.write(self.style.SUCCESS('Des créneaux existent déjà.'))
            return
        Creneau.objects.create(nom='Mercredi matin', jour='Mercredi', heure_debut='09:00', heure_fin='12:00')
        Creneau.objects.create(nom='Samedi après-midi', jour='Samedi', heure_debut='14:00', heure_fin='17:00')
        self.stdout.write(self.style.SUCCESS('Créneaux de test créés.'))
