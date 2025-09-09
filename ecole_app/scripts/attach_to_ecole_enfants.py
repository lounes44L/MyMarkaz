from django.core.management.base import BaseCommand
from ecole_app.models import Composante, AnneeScolaire, Professeur, Classe, Eleve, ListeAttente, Paiement, Charge, PresenceEleve, PresenceProfesseur, CarnetPedagogique

class Command(BaseCommand):
    help = "Associe toutes les données existantes à la composante 'École Enfants'"

    def handle(self, *args, **options):
        composante, created = Composante.objects.get_or_create(
            nom='École Enfants',
            defaults={'description': 'Composante par défaut', 'active': True}
        )
        self.stdout.write(self.style.SUCCESS(f"Composante utilisée : {composante} (créée : {created})"))

        models_to_update = [
            AnneeScolaire, Professeur, Classe, Eleve, ListeAttente, Paiement, Charge, PresenceEleve, PresenceProfesseur, CarnetPedagogique
        ]
        for model in models_to_update:
            updated = model.objects.filter(composante__isnull=True).update(composante=composante)
            self.stdout.write(f"{model.__name__}: {updated} objets mis à jour.")

        self.stdout.write(self.style.SUCCESS("Toutes les données existantes sont désormais rattachées à 'École Enfants'."))
