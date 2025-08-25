from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('ecole_app', '0003_anneescolaire_eleve_user_professeur_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='revision',
            name='remarques',
            field=models.TextField(blank=True, help_text='Commentaires ou détails sur la révision', null=True),
        ),
    ]
