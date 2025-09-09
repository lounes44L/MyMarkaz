# Generated manually to fix migration conflicts and create ParametreSite table

from django.db import migrations, models


def create_parametresite_if_not_exists(apps, schema_editor):
    """Create ParametreSite table if it doesn't exist"""
    try:
        # Check if table exists
        schema_editor.execute("SELECT 1 FROM ecole_app_parametresite LIMIT 1")
    except Exception:
        # Table doesn't exist, create it
        schema_editor.execute("""
            CREATE TABLE ecole_app_parametresite (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                montant_defaut_eleve DECIMAL(10, 2) NOT NULL DEFAULT 200.00,
                date_modification DATETIME NOT NULL
            )
        """)
        schema_editor.execute("""
            INSERT INTO ecole_app_parametresite (montant_defaut_eleve, date_modification)
            VALUES (200.00, datetime('now'))
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('ecole_app', '0042_merge_20250822_1353'),
    ]

    operations = [
        migrations.RunPython(create_parametresite_if_not_exists),
    ]
