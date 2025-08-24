import os
import sys
import django

# Ajout du dossier projet au PYTHONPATH pour import Windows
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_markaz.settings')
    django.setup()
    from ecole_app.models import Eleve
    from django.contrib.auth.models import User
    import random, string

    def generer_mot_de_passe():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    count = 0
    for eleve in Eleve.objects.filter(mot_de_passe_en_clair__isnull=True):
        if not eleve.user:
            continue
        new_password = generer_mot_de_passe()
        eleve.user.set_password(new_password)
        eleve.user.save()
        eleve.mot_de_passe_en_clair = new_password
        eleve.save()
        print(f"[OK] Mot de passe fixé pour {eleve.nom} {eleve.prenom} (id={eleve.id}) : {new_password}")
        count += 1
    print(f"Correction terminée. {count} élèves corrigés.")

if __name__ == '__main__':
    main()
