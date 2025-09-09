from django.core.management.base import BaseCommand
from ecole_app.models import Professeur, Classe, Eleve, Paiement, Creneau
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Crée des données de test pour l\'application'

    def handle(self, *args, **options):
        # Créer des créneaux s'ils n'existent pas
        if not Creneau.objects.exists():
            self.stdout.write('Création des créneaux...')
            creneaux = [
                Creneau.objects.create(nom='Lundi matin', jour='Lundi', heure_debut='09:00', heure_fin='12:00'),
                Creneau.objects.create(nom='Mercredi après-midi', jour='Mercredi', heure_debut='14:00', heure_fin='17:00'),
                Creneau.objects.create(nom='Samedi matin', jour='Samedi', heure_debut='09:00', heure_fin='12:00')
            ]
        else:
            creneaux = list(Creneau.objects.all())
            self.stdout.write('Des créneaux existent déjà.')

        # Créer des professeurs s'ils n'existent pas
        if not Professeur.objects.exists():
            self.stdout.write('Création des professeurs...')
            professeurs = [
                Professeur.objects.create(nom='Dupont', prenom='Jean', specialite='Arabe littéraire', telephone='0612345678', email='jean.dupont@example.com'),
                Professeur.objects.create(nom='Martin', prenom='Sophie', specialite='Coran', telephone='0687654321', email='sophie.martin@example.com'),
                Professeur.objects.create(nom='Lefebvre', prenom='Thomas', specialite='Education islamique', telephone='0611223344', email='thomas.lefebvre@example.com')
            ]
        else:
            professeurs = list(Professeur.objects.all())
            self.stdout.write('Des professeurs existent déjà.')

        # Créer des classes s'ils n'existent pas
        if not Classe.objects.exists():
            self.stdout.write('Création des classes...')
            classes = [
                Classe.objects.create(nom='Débutant', niveau='A1', capacite=15, professeur=random.choice(professeurs), creneau=random.choice(creneaux)),
                Classe.objects.create(nom='Intermédiaire', niveau='B1', capacite=12, professeur=random.choice(professeurs), creneau=random.choice(creneaux)),
                Classe.objects.create(nom='Avancé', niveau='C1', capacite=10, professeur=random.choice(professeurs), creneau=random.choice(creneaux))
            ]
        else:
            classes = list(Classe.objects.all())
            self.stdout.write('Des classes existent déjà.')

        # Créer des élèves s'ils n'existent pas
        if Eleve.objects.count() < 5:
            self.stdout.write('Création des élèves...')
            noms = ['Petit', 'Dubois', 'Leroy', 'Moreau', 'Simon', 'Laurent', 'Michel', 'Garcia']
            prenoms = ['Emma', 'Lucas', 'Chloé', 'Hugo', 'Inès', 'Nathan', 'Léa', 'Théo']
            
            for i in range(10):
                Eleve.objects.create(
                    nom=random.choice(noms),
                    prenom=random.choice(prenoms),
                    classe=random.choice(classes),
                    creneau=random.choice(creneaux),
                    date_naissance=f"200{random.randint(0, 9)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                    telephone=f"06{random.randint(10000000, 99999999)}",
                    email=f"eleve{i}@example.com",
                    adresse=f"{random.randint(1, 100)} rue de Paris, 75000 Paris"
                )
        else:
            self.stdout.write('Des élèves existent déjà.')

        # Créer des paiements s'ils n'existent pas
        if not Paiement.objects.exists():
            self.stdout.write('Création des paiements...')
            eleves = list(Eleve.objects.all())
            methodes = ['Espèces', 'Chèque', 'Virement', 'Carte bancaire']
            
            for eleve in eleves[:5]:  # Créer des paiements pour les 5 premiers élèves
                for i in range(1, 4):  # 3 paiements par élève
                    mois = random.randint(1, 12)
                    Paiement.objects.create(
                        eleve=eleve,
                        montant=random.choice([30, 40, 50]),
                        date=timezone.now().replace(month=mois),
                        methode=random.choice(methodes).lower(),
                        commentaire=f"Paiement du mois {mois}/2025"
                    )
        else:
            self.stdout.write('Des paiements existent déjà.')

        self.stdout.write(self.style.SUCCESS('Données de test créées avec succès !'))
