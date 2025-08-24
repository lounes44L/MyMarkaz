# Manual migration to create ParametreSite table and handle conflicts

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecole_app', '0042_merge_20250822_1353'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParametreSite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('montant_defaut_eleve', models.DecimalField(decimal_places=2, default=200.0, help_text='Montant par défaut pour les nouveaux élèves en euros', max_digits=10)),
                ('date_modification', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Paramètre du site',
                'verbose_name_plural': 'Paramètres du site',
            },
        ),
    ]
