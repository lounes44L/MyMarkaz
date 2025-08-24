from django.core.management.base import BaseCommand
from ecole_app.models import Composante, AnneeScolaire
from datetime import date

class Command(BaseCommand):
    help = "Crée une année scolaire active pour chaque composante sans année scolaire."

    def handle(self, *args, **options):
        for composante in Composante.objects.filter(active=True):
            if not AnneeScolaire.objects.filter(composante=composante).exists():
                annee = f"{date.today().year}-{date.today().year+1}"
                AnneeScolaire.objects.create(
                    composante=composante,
                    nom=annee,
                    date_debut=date(date.today().year, 9, 1),
                    date_fin=date(date.today().year+1, 6, 30),
                    active=True
                )
                self.stdout.write(self.style.SUCCESS(f"Année scolaire créée pour {composante.nom}"))
            else:
                self.stdout.write(f"Composante {composante.nom} a déjà une année scolaire.")
        self.stdout.write(self.style.SUCCESS("Vérification terminée."))
