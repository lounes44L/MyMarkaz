# Script pour corriger l'association des créneaux aux composantes
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gestion_markaz.settings")
django.setup()

from ecole_app.models import Creneau, Classe, Composante

def fix_creneaux():
    # Trouver la composante "École Enfants"
    try:
        ecole_enfants = Composante.objects.get(nom__icontains='enfant')
        print(f"Composante École Enfants trouvée avec ID: {ecole_enfants.id}")
    except Composante.DoesNotExist:
        print("Composante École Enfants non trouvée!")
        return
    except Composante.MultipleObjectsReturned:
        ecole_enfants = Composante.objects.filter(nom__icontains='enfant').first()
        print(f"Plusieurs composantes trouvées, utilisation de la première: {ecole_enfants.id} - {ecole_enfants.nom}")
    
    # Afficher tous les créneaux existants
    print("\n=== CRÉNEAUX AVANT CORRECTION ===")
    for c in Creneau.objects.all():
        print(f"ID: {c.id}, Nom: {c.nom}, Composante ID: {c.composante_id}")
    
    # Identifier les créneaux utilisés par les classes de la composante École Enfants
    classes_ecole_enfants = Classe.objects.filter(composante_id=ecole_enfants.id)
    print(f"\nNombre de classes dans École Enfants: {classes_ecole_enfants.count()}")
    
    creneaux_a_corriger = set()
    for classe in classes_ecole_enfants:
        if classe.creneau:
            print(f"Classe: {classe.nom}, utilise le créneau: {classe.creneau.nom} (ID: {classe.creneau.id})")
            creneaux_a_corriger.add(classe.creneau.id)
    
    # Corriger les créneaux pour les associer à École Enfants
    print("\n=== CORRECTION DES CRÉNEAUX ===")
    for creneau_id in creneaux_a_corriger:
        creneau = Creneau.objects.get(id=creneau_id)
        old_composante = creneau.composante_id
        creneau.composante_id = ecole_enfants.id
        creneau.save()
        print(f"Créneau {creneau.nom} (ID: {creneau.id}) : Composante changée de {old_composante} à {ecole_enfants.id}")
    
    # Afficher tous les créneaux après correction
    print("\n=== CRÉNEAUX APRÈS CORRECTION ===")
    for c in Creneau.objects.all():
        print(f"ID: {c.id}, Nom: {c.nom}, Composante ID: {c.composante_id}")

if __name__ == "__main__":
    fix_creneaux()
    print("\nCorrection terminée. Veuillez rafraîchir la page des créneaux pour voir les changements.")
