from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecole_app', '0039_merge_20250821_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='presenceprofesseur',
            name='creneau',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='presences_professeurs', to='ecole_app.creneau'),
        ),
        migrations.AlterUniqueTogether(
            name='presenceprofesseur',
            unique_together={('professeur', 'date', 'creneau')},
        ),
    ]
