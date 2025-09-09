# Script complet pour diagnostiquer et corriger l'association des créneaux aux composantes
import os
import django
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gestion_markaz.settings")
django.setup()

from ecole_app.models import Creneau, Classe, Composante

def diagnostic_et_correction():
    # Afficher les composantes
    print("=== COMPOSANTES ===")
    composantes = {}
    for comp in Composante.objects.all():
        print(f"ID: {comp.id}, Nom: {comp.nom}")
        composantes[comp.id] = comp.nom
    
    # Trouver la composante "École Enfants"
    ecole_enfants_id = None
    for comp_id, comp_nom in composantes.items():
        if "enfant" in comp_nom.lower():
            ecole_enfants_id = comp_id
            print(f"\nComposante École Enfants identifiée: ID={ecole_enfants_id}, Nom={comp_nom}")
            break
    
    if not ecole_enfants_id:
        print("ERREUR: Impossible de trouver la composante 'École Enfants'")
        sys.exit(1)
    
    # Afficher tous les créneaux existants
    print("\n=== CRÉNEAUX AVANT CORRECTION ===")
    creneaux = {}
    for c in Creneau.objects.all():
        comp_nom = composantes.get(c.composante_id, "Non associé")
        print(f"ID: {c.id}, Nom: {c.nom}, Jour: {c.jour}, Composante: {comp_nom} (ID: {c.composante_id})")
        creneaux[c.id] = {"nom": c.nom, "composante_id": c.composante_id}
    
    # Identifier les classes de la composante École Enfants et leurs créneaux
    print("\n=== CLASSES DE LA COMPOSANTE ÉCOLE ENFANTS ===")
    classes_ecole = Classe.objects.filter(composante_id=ecole_enfants_id)
    print(f"Nombre de classes dans École Enfants: {classes_ecole.count()}")
    
    creneaux_a_corriger = set()
    for classe in classes_ecole:
        if classe.creneau:
            comp_nom = composantes.get(classe.creneau.composante_id, "Non associé")
            print(f"Classe: {classe.nom}, Créneau: {classe.creneau.nom} (ID: {classe.creneau.id}), "
                  f"Composante du créneau: {comp_nom} (ID: {classe.creneau.composante_id})")
            
            # Si le créneau n'est pas associé à École Enfants, on le marque pour correction
            if classe.creneau.composante_id != ecole_enfants_id:
                creneaux_a_corriger.add(classe.creneau.id)
    
    # Corriger les créneaux pour les associer à École Enfants
    if creneaux_a_corriger:
        print("\n=== CORRECTION DES CRÉNEAUX ===")
        for creneau_id in creneaux_a_corriger:
            creneau = Creneau.objects.get(id=creneau_id)
            old_composante_id = creneau.composante_id
            old_composante_nom = composantes.get(old_composante_id, "Non associé")
            
            creneau.composante_id = ecole_enfants_id
            creneau.save()
            
            print(f"Créneau {creneau.nom} (ID: {creneau.id}): "
                  f"Composante changée de '{old_composante_nom}' (ID: {old_composante_id}) "
                  f"à 'École Enfants' (ID: {ecole_enfants_id})")
    else:
        print("\nAucun créneau à corriger - tous les créneaux des classes sont déjà associés à École Enfants")
    
    # Vérifier s'il y a des créneaux sans composante
    creneaux_sans_composante = Creneau.objects.filter(composante_id__isnull=True)
    if creneaux_sans_composante.exists():
        print("\n=== CRÉNEAUX SANS COMPOSANTE ===")
        for c in creneaux_sans_composante:
            print(f"ID: {c.id}, Nom: {c.nom}, Jour: {c.jour}")
            c.composante_id = ecole_enfants_id
            c.save()
            print(f"  → Associé à École Enfants (ID: {ecole_enfants_id})")
    
    # Afficher tous les créneaux après correction
    print("\n=== CRÉNEAUX APRÈS CORRECTION ===")
    for c in Creneau.objects.all():
        comp_nom = composantes.get(c.composante_id, "Non associé")
        print(f"ID: {c.id}, Nom: {c.nom}, Jour: {c.jour}, Composante: {comp_nom} (ID: {c.composante_id})")
    
    # Compter les créneaux par composante
    print("\n=== NOMBRE DE CRÉNEAUX PAR COMPOSANTE ===")
    for comp_id, comp_nom in composantes.items():
        count = Creneau.objects.filter(composante_id=comp_id).count()
        print(f"{comp_nom} (ID: {comp_id}): {count} créneaux")

if __name__ == "__main__":
    diagnostic_et_correction()
    print("\nDiagnostic et correction terminés. Veuillez rafraîchir la page des créneaux pour voir les changements.")
