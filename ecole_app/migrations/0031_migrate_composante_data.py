from django.db import migrations

def migrate_composante_to_composantes(apps, schema_editor):
    """
    Migre les données de l'ancien champ ForeignKey 'composante' 
    vers le nouveau champ ManyToMany 'composantes'
    """
    Professeur = apps.get_model('ecole_app', 'Professeur')
    
    # Pour chaque professeur, ajouter sa composante actuelle à ses composantes
    for professeur in Professeur.objects.all():
        if professeur.composante:
            professeur.composantes.add(professeur.composante)
            print(f"Migré professeur {professeur.nom} : composante {professeur.composante.nom} ajoutée à composantes")


class Migration(migrations.Migration):

    dependencies = [
        ('ecole_app', '0030_add_composantes_manytomany'),
    ]

    operations = [
        migrations.RunPython(migrate_composante_to_composantes),
    ]
