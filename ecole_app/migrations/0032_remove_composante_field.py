from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('ecole_app', '0031_migrate_composante_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='professeur',
            name='composante',
        ),
    ]
