from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import Eleve, Professeur, generer_identifiant, generer_mot_de_passe
import re


@receiver(post_save, sender=Eleve)
def create_user_for_eleve(sender, instance, created, **kwargs):
    """Crée automatiquement un compte utilisateur pour un élève nouvellement créé"""
    if created and not instance.user:
        # Générer un identifiant au format nom.prenom
        nom = instance.nom.lower() if instance.nom else ''
        prenom = instance.prenom.lower() if instance.prenom else ''
        
        # Nettoyer les caractères spéciaux et espaces
        nom = re.sub(r'[^a-z0-9]', '', nom)
        prenom = re.sub(r'[^a-z0-9]', '', prenom)
        
        # Créer l'identifiant au format nom.prenom
        username = f"{nom}.{prenom}" if nom and prenom else generer_identifiant('E')
        
        # Créer le mot de passe au format nom.prenom1
        password = f"{nom}.{prenom}1" if nom and prenom else generer_mot_de_passe()
        
        # S'il n'y a pas d'email, on utilise un identifiant par défaut
        email = instance.email or f"{username}@markaz-quran.local"
        
        # Vérifier si le username existe déjà, ajouter un chiffre si nécessaire
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=instance.prenom,
            last_name=instance.nom
        )
        
        # Associer au groupe "Élèves" (le créer s'il n'existe pas)
        eleve_group, _ = Group.objects.get_or_create(name='Élèves')
        user.groups.add(eleve_group)

        # Lier l'utilisateur à l'élève
        instance.user = user

        # Stocker le mot de passe en clair pour l'affichage permanent
        instance.mot_de_passe_en_clair = password

        # Sauvegarder sans appeler le signal à nouveau
        post_save.disconnect(create_user_for_eleve, sender=Eleve)
        instance.save()
        post_save.connect(create_user_for_eleve, sender=Eleve)

@receiver(post_save, sender=Professeur)
def create_user_for_professeur(sender, instance, created, **kwargs):
    """Crée automatiquement un compte utilisateur pour un professeur nouvellement créé"""
    if created and not instance.user:
        # S'il n'y a pas d'email, on utilise un identifiant par défaut
        email = instance.email or f"{generer_identifiant('P')}@markaz-quran.local"
        username = generer_identifiant('P')
        password = generer_mot_de_passe()

        # Vérifier si le username existe déjà
        while User.objects.filter(username=username).exists():
            username = generer_identifiant('P')

        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            last_name=instance.nom
        )

        # Associer au groupe "Professeurs" (le créer s'il n'existe pas)
        prof_group, _ = Group.objects.get_or_create(name='Professeurs')
        user.groups.add(prof_group)

        # Lier l'utilisateur au professeur
        instance.user = user

        # Stocker le mot de passe en clair pour l'affichage permanent
        instance.mot_de_passe_en_clair = password

        # Sauvegarder sans appeler le signal à nouveau
        post_save.disconnect(create_user_for_professeur, sender=Professeur)
        instance.save()
        post_save.connect(create_user_for_professeur, sender=Professeur)
