from django.db import migrations

def fix_professeur_composantes(apps, schema_editor):
    """
    Cette fonction corrige les associations entre professeurs et composantes.
    Elle s'assure que chaque professeur est correctement associé à au moins une composante.
    """
    Professeur = apps.get_model('ecole_app', 'Professeur')
    Composante = apps.get_model('ecole_app', 'Composante')
    
    # Récupérer toutes les composantes
    composantes = list(Composante.objects.all())
    if not composantes:
        print("Aucune composante trouvée. Impossible de corriger les associations.")
        return
    
    # Composante par défaut (première composante)
    default_composante = composantes[0]
    
    # Pour chaque professeur
    for professeur in Professeur.objects.all():
        # Vérifier s'il a des composantes
        if professeur.composantes.count() == 0:
            print(f"Correction pour le professeur {professeur.id}: {professeur.nom}")
            # Ajouter la composante par défaut
            professeur.composantes.add(default_composante)
            print(f"  -> Ajout de la composante {default_composante.id}: {default_composante.nom}")


class Migration(migrations.Migration):

    dependencies = [
        ('ecole_app', '0032_remove_composante_field'),
    ]

    operations = [
        migrations.RunPython(fix_professeur_composantes),
    ]
