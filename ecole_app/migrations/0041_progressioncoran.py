from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecole_app', '0039_merge_20250821_1406'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgressionCoran',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sourate_actuelle', models.CharField(blank=True, help_text='Sourate actuellement en cours de mémorisation', max_length=100, null=True)),
                ('page_actuelle', models.PositiveIntegerField(default=1, help_text='Dernière page mémorisée')),
                ('direction_memorisation', models.CharField(choices=[('debut', 'Du début (Al-Baqara)'), ('fin', 'De la fin (An-Nas)')], default='debut', help_text='Direction de mémorisation (du début ou de la fin du Coran)', max_length=10)),
                ('date_mise_a_jour', models.DateTimeField(auto_now=True)),
                ('eleve', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='progression_coran', to='ecole_app.eleve')),
            ],
            options={
                'verbose_name': 'Progression du Coran',
                'verbose_name_plural': 'Progressions du Coran',
            },
        ),
    ]
