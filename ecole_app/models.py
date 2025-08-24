from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.models import User
import random
import string
from datetime import date

# Modèles pour la gestion de l'école

class ParametreSite(models.Model):
    montant_defaut_eleve = models.DecimalField(max_digits=10, decimal_places=2, default=200.00, 
                                            help_text="Montant par défaut pour les nouveaux élèves en euros")
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Paramètre du site"
        verbose_name_plural = "Paramètres du site"
    
    def __str__(self):
        return f"Paramètres du site (modifié le {self.date_modification.strftime('%d/%m/%Y')})"
    
    @classmethod
    def get_montant_defaut(cls):
        params = cls.objects.first()
        if not params:
            params = cls.objects.create()
        return params.montant_defaut_eleve


class Composante(models.Model):
    nom = models.CharField(max_length=100, unique=True, help_text="Nom de la composante (ex: École Enfants, École Adultes, etc.)")
    description = models.TextField(blank=True, help_text="Description de la composante")
    active = models.BooleanField(default=True, help_text="Composante active ou non")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name = "Composante"
        verbose_name_plural = "Composantes"
        ordering = ['nom']

class Creneau(models.Model):
    JOURS_SEMAINE = [
        ('lundi', 'Lundi'),
        ('mardi', 'Mardi'),
        ('mercredi', 'Mercredi'),
        ('jeudi', 'Jeudi'),
        ('vendredi', 'Vendredi'),
        ('samedi', 'Samedi'),
        ('dimanche', 'Dimanche'),
    ]
    
    composante = models.ForeignKey(Composante, on_delete=models.CASCADE, related_name='creneaux', null=True, blank=True)
    nom = models.CharField(max_length=100)
    jour = models.CharField(max_length=10, choices=JOURS_SEMAINE, blank=True, null=True)
    heure_debut = models.TimeField(blank=True, null=True)
    heure_fin = models.TimeField(blank=True, null=True)
    archive = models.BooleanField(default=False, help_text="Archivé (non proposé dans les formulaires)")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nom
    
    @property
    def nb_eleves(self):
        return sum(classe.eleves.count() for classe in self.classes.all())

    class Meta:
        verbose_name = "Créneau"
        verbose_name_plural = "Créneaux"

class AnneeScolaire(models.Model):
    composante = models.ForeignKey(Composante, on_delete=models.CASCADE, related_name='annees_scolaires', null=True, blank=True)
    nom = models.CharField(max_length=100, help_text="Exemple: 2024-2025")
    date_debut = models.DateField()
    date_fin = models.DateField()
    active = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nom
    
    def save(self, *args, **kwargs):
        # Si cette année est active, désactiver les autres
        if self.active:
            AnneeScolaire.objects.exclude(pk=self.pk).update(active=False)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Année scolaire"
        verbose_name_plural = "Années scolaires"

class Professeur(models.Model):
    # Relation Many-to-Many pour permettre à un professeur d'enseigner dans plusieurs composantes
    composantes = models.ManyToManyField(Composante, related_name='professeurs', blank=True, help_text="Composantes où enseigne ce professeur")
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='professeur')
    nom = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    mot_de_passe_en_clair = models.CharField(max_length=100, blank=True, null=True, help_text="Mot de passe en clair (non sécurisé)")
    indemnisation = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, help_text="Indemnisation mensuelle")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nom
    
    def get_all_classes(self):
        """Retourne toutes les classes du professeur dans toutes ses composantes"""
        return self.classes.all()
    
    def get_all_eleves(self):
        """Retourne tous les élèves du professeur dans toutes ses composantes"""
        from django.db.models import Q
        classes_ids = self.classes.values_list('id', flat=True)
        return Eleve.objects.filter(classes__in=classes_ids).distinct()
    
    def get_composantes_list(self):
        """Retourne la liste des noms des composantes du professeur"""
        return ", ".join([comp.nom for comp in self.composantes.all()])
     
    
    class Meta:
        verbose_name = "Professeur"
        verbose_name_plural = "Professeurs"

class Classe(models.Model):
    composante = models.ForeignKey(Composante, on_delete=models.CASCADE, related_name='classes', null=True, blank=True)
    nom = models.CharField(max_length=100)
    professeur = models.ForeignKey(Professeur, on_delete=models.SET_NULL, null=True, related_name='classes')
    creneau = models.ForeignKey(Creneau, on_delete=models.SET_NULL, null=True, related_name='classes')
    capacite = models.IntegerField(default=20)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.SET_NULL, null=True, blank=True, related_name='classes')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nom
    
    def taux_occupation(self):
        # Compter les élèves liés par ForeignKey (ancienne relation)
        eleves_fk_count = self.eleves.filter(archive=False).count()
        # Compter les élèves liés par ManyToManyField (nouvelle relation)
        eleves_m2m_count = self.eleves_multi.filter(archive=False).count()
        # Utiliser le nombre total d'élèves (somme des deux relations)
        total_eleves = eleves_fk_count + eleves_m2m_count
        return min(100, round((total_eleves / self.capacite) * 100)) if self.capacite > 0 else 0
        
    def get_total_eleves(self):
        """Retourne le nombre total d'élèves dans cette classe (ForeignKey + ManyToManyField)"""
        eleves_fk_count = self.eleves.filter(archive=False).count()
        eleves_m2m_count = self.eleves_multi.filter(archive=False).count()
        return eleves_fk_count + eleves_m2m_count
    
    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"

class Eleve(models.Model):
    classes = models.ManyToManyField('Classe', related_name='eleves_multi', blank=True)  # Ajout pour multi-classes
    composante = models.ForeignKey(Composante, on_delete=models.CASCADE, related_name='eleves', null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='eleve')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, blank=True)
    prenom_pere = models.CharField(max_length=100, blank=True, null=True, help_text="Prénom du père")
    prenom_mere = models.CharField(max_length=100, blank=True, null=True, help_text="Prénom de la mère")
    mot_de_passe_en_clair = models.CharField(max_length=100, blank=True, null=True, help_text="Mot de passe en clair (non sécurisé)")
    classe = models.ForeignKey(Classe, on_delete=models.SET_NULL, null=True, related_name='eleves')
    creneaux = models.ManyToManyField(Creneau, related_name='eleves', blank=True)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.SET_NULL, null=True, blank=True, related_name='eleves')
    date_naissance = models.DateField(null=True, blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    telephone_secondaire = models.CharField(max_length=20, blank=True, null=True, help_text="Numéro de téléphone secondaire")
    adresse = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    remarque = models.TextField(blank=True, null=True, help_text="Remarque libre sur l'élève")
    archive = models.BooleanField(default=False, help_text="Élève archivé")
    motif_archive = models.TextField(blank=True, null=True, help_text="Motif d'archivage")
    date_creation = models.DateTimeField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=200.00, help_text="Montant total à payer pour l'inscription")
    
    def __str__(self):
        return f"{self.nom} {self.prenom}".strip()
    
    @property
    def age(self):
        """Calcule l'âge de l'élève à partir de sa date de naissance"""
        if not self.date_naissance:
            return None
        today = date.today()
        return today.year - self.date_naissance.year - ((today.month, today.day) < (self.date_naissance.month, self.date_naissance.day))
    
    @property
    def montant_paye(self):
        """Calcule le montant total payé par l'élève"""
        return self.paiements.aggregate(total=models.Sum('montant')).get('total') or 0
    
    @property
    def montant_restant(self):
        """Calcule le montant restant à payer par l'élève"""
        return self.montant_total - self.montant_paye
    
    class Meta:
        verbose_name = "Élève"
        verbose_name_plural = "Élèves"

class ListeAttente(models.Model):
    composante = models.ForeignKey(Composante, on_delete=models.CASCADE, related_name='liste_attente', null=True, blank=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    remarque = models.TextField(blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)
    ajoute_definitivement = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nom} {self.prenom} (attente)"

    class Meta:
        verbose_name = "Enfant en liste d'attente"
        verbose_name_plural = "Liste d'attente"

class Paiement(models.Model):
    METHODES = (
        ('especes', 'Espèces'),
        ('cheque', 'Chèque'),
        ('virement', 'Virement'),
        ('carte', 'Carte bancaire'),
    )
    
    composante = models.ForeignKey(Composante, on_delete=models.CASCADE, related_name='paiements', null=True, blank=True)
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    methode = models.CharField(max_length=20, choices=METHODES, default='especes')
    commentaire = models.TextField(blank=True)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.SET_NULL, null=True, blank=True, related_name='paiements')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.eleve} - {self.montant}€ ({self.date})"
    
    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"

class Charge(models.Model):
    CATEGORIES = (
        ('loyer', 'Loyer'),
        ('electricite', 'Électricité'),
        ('eau', 'Eau'),
        ('internet', 'Internet'),
        ('fournitures', 'Fournitures'),
        ('indemnisation', 'Indemnisation professeur'),
        ('autre', 'Autre'),
    )
    
    composante = models.ForeignKey(Composante, on_delete=models.CASCADE, related_name='charges', null=True, blank=True)
    categorie = models.CharField(max_length=20, choices=CATEGORIES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    date = models.DateField(default=timezone.now)
    professeur = models.ForeignKey(Professeur, on_delete=models.SET_NULL, null=True, blank=True, related_name='indemnisations')
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.SET_NULL, null=True, blank=True, related_name='charges')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.categorie == 'indemnisation' and self.professeur:
            return f"Indemnisation {self.professeur} - {self.montant}€ ({self.date})"
        return f"{self.get_categorie_display()} - {self.montant}€ ({self.date})"
    
    class Meta:
        verbose_name = "Charge"
        verbose_name_plural = "Charges"

class PresenceEleve(models.Model):
    composante = models.ForeignKey(Composante, on_delete=models.CASCADE, related_name='presences_eleves', null=True, blank=True)
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE, related_name='presences')
    date = models.DateField()
    present = models.BooleanField(default=True)
    justifie = models.BooleanField(default=False)
    commentaire = models.TextField(blank=True)
    classe = models.ForeignKey(Classe, on_delete=models.SET_NULL, null=True, related_name='presences_eleves')
    creneau = models.ForeignKey(Creneau, on_delete=models.SET_NULL, null=True, related_name='presences_eleves')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Présence élève"
        verbose_name_plural = "Présences élèves"
        unique_together = ['eleve', 'date', 'classe']

class PresenceProfesseur(models.Model):
    composante = models.ForeignKey(Composante, on_delete=models.CASCADE, related_name='presences_professeurs', null=True, blank=True)
    professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE, related_name='presences')
    date = models.DateField()
    creneau = models.ForeignKey(Creneau, on_delete=models.SET_NULL, null=True, blank=True, related_name='presences_professeurs')
    present = models.BooleanField(default=True)
    justifie = models.BooleanField(default=False)
    commentaire = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Présence professeur"
        verbose_name_plural = "Présences professeurs"
        unique_together = ['professeur', 'date', 'creneau']

def generer_identifiant(prefix):
    """Génère un identifiant simple basé sur le préfixe (E pour élève, P pour professeur) et un nombre aléatoire"""
    annee_actuelle = timezone.now().year % 100  # Derniers deux chiffres de l'année
    random_digits = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{annee_actuelle}{random_digits}"

def generer_mot_de_passe():
    """Génère un mot de passe simple composé de lettres et chiffres"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


# Modèles pour le carnet pédagogique

class CarnetPedagogique(models.Model):
    """Carnet pédagogique principal pour chaque élève"""
    composante = models.ForeignKey(Composante, on_delete=models.CASCADE, related_name='carnets_pedagogiques', null=True, blank=True)
    eleve = models.OneToOneField(Eleve, on_delete=models.CASCADE, related_name='carnet_pedagogique')
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Carnet de {self.eleve}"
    
    class Meta:
        verbose_name = "Carnet pédagogique"
        verbose_name_plural = "Carnets pédagogiques"

class EcouteAvantMemo(models.Model):
    """Modèle pour le suivi des séances d'écoute avant mémorisation"""
    carnet = models.ForeignKey(CarnetPedagogique, on_delete=models.CASCADE, related_name='ecoutes')
    date = models.DateField()
    debut_page = models.PositiveIntegerField()
    fin_page = models.PositiveIntegerField()
    enseignant = models.ForeignKey(Professeur, on_delete=models.SET_NULL, null=True, related_name='ecoutes_supervisees')
    remarques = models.TextField(blank=True)
    
    def __str__(self):
        return f"Écoute {self.carnet.eleve} - Pages {self.debut_page}-{self.fin_page} ({self.date})"
    
    class Meta:
        verbose_name = "Écoute avant mémorisation"
        verbose_name_plural = "Écoutes avant mémorisation"

class Memorisation(models.Model):
    """Modèle pour le suivi des séances de mémorisation"""
    carnet = models.ForeignKey(CarnetPedagogique, on_delete=models.CASCADE, related_name='memorisations')
    date = models.DateField()
    debut_page = models.PositiveIntegerField()
    fin_page = models.PositiveIntegerField()
    enseignant = models.ForeignKey(Professeur, on_delete=models.SET_NULL, null=True, related_name='memorisations_supervisees')
    remarques = models.TextField(blank=True)
    
    def __str__(self):
        return f"Mémorisation {self.carnet.eleve} - Pages {self.debut_page}-{self.fin_page} ({self.date})"
    
    class Meta:
        verbose_name = "Mémorisation"
        verbose_name_plural = "Mémorisations"

class Revision(models.Model):
    """Modèle pour le suivi des révisions hebdomadaires"""
    JOURS_SEMAINE = [
        ('lundi', 'Lundi'),
        ('mardi', 'Mardi'),
        ('mercredi', 'Mercredi'),
        ('jeudi', 'Jeudi'),
        ('vendredi', 'Vendredi'),
        ('samedi', 'Samedi'),
        ('dimanche', 'Dimanche'),
    ]
    
    carnet = models.ForeignKey(CarnetPedagogique, on_delete=models.CASCADE, related_name='revisions')
    semaine = models.PositiveIntegerField(help_text="Numéro de la semaine dans l'année")
    date = models.DateField()
    jour = models.CharField(max_length=10, choices=JOURS_SEMAINE)
    nombre_hizb = models.DecimalField(max_digits=4, decimal_places=2, default=0, help_text="Nombre de Hizb révisés (décimal autorisé)")
    
    def __str__(self):
        return f"Révision {self.carnet.eleve} - {self.get_jour_display()} S{self.semaine} ({self.nombre_hizb} hizb)"
    
    class Meta:
        verbose_name = "Révision"
        verbose_name_plural = "Révisions"

class Repetition(models.Model):
    """Modèle pour le suivi des répétitions par page et par sourate"""
    carnet = models.ForeignKey(CarnetPedagogique, on_delete=models.CASCADE, related_name='repetitions')
    sourate = models.CharField(max_length=100)
    page = models.PositiveIntegerField()
    nombre_repetitions = models.PositiveIntegerField(default=0)
    derniere_date = models.DateField(auto_now=True)
    
    def __str__(self):
        return f"Répétition {self.carnet.eleve} - {self.sourate} Page {self.page} ({self.nombre_repetitions} fois)"
    
    class Meta:
        verbose_name = "Répétition"
        verbose_name_plural = "Répétitions"

class SiteConfig(models.Model):
    key = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=255, default='default')

    def __str__(self):
        return f"{self.key}: {self.value}"
    
    @classmethod
    def get_site_name(cls):
        site_config = cls.objects.filter(key='site_name').first()
        return site_config.value if site_config else 'École Markaz'
        
    @classmethod
    def set_site_name(cls, name):
        site_config, created = cls.objects.get_or_create(key='site_name')
        site_config.value = name
        site_config.save()
        return site_config

    class Meta:
        verbose_name = "Configuration du site"
        verbose_name_plural = "Configurations du site"


class CompetenceLivre(models.Model):
    """Modèle pour les compétences à évaluer dans le livre"""
    LECON_CHOICES = [
        (0, 'Règles de base'),
        (1, 'Leçon 1'),
        (2, 'Leçon 2'),
        (3, 'Leçon 3'),
        (4, 'Leçon 4'),
        (5, 'Leçon 5'),
        (6, 'Leçon 6'),
        (7, 'Leçon 7'),
        (8, 'Leçon 8'),
    ]
    
    lecon = models.IntegerField(choices=LECON_CHOICES, help_text="Numéro de la leçon")
    description = models.TextField(help_text="Description de la compétence")
    ordre = models.IntegerField(default=0, help_text="Ordre d'affichage de la compétence")
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Leçon {self.get_lecon_display()} - {self.description[:30]}..."
    
    class Meta:
        verbose_name = "Compétence du livre"
        verbose_name_plural = "Compétences du livre"
        ordering = ['lecon', 'ordre']


class EvaluationCompetence(models.Model):
    """Modèle pour l'évaluation des compétences des élèves"""
    STATUT_CHOICES = [
        ('acquis', 'Acquis'),
        ('non_acquis', 'Non Acquis'),
        ('en_cours', 'En cours'),
    ]
    
    eleve = models.ForeignKey('Eleve', on_delete=models.CASCADE, related_name='evaluations_competences')
    competence = models.ForeignKey(CompetenceLivre, on_delete=models.CASCADE, related_name='evaluations')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_cours')
    date_evaluation = models.DateField(default=date.today)
    commentaire = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.eleve} - {self.competence} - {self.get_statut_display()}"
    
    class Meta:
        verbose_name = "Évaluation de compétence"
        verbose_name_plural = "Évaluations de compétences"
        unique_together = ['eleve', 'competence']
        ordering = ['eleve', 'competence__lecon', 'competence__ordre']

class PaiementHistorique(models.Model):
    paiement = models.ForeignKey('Paiement', on_delete=models.CASCADE, related_name='historiques')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    methode = models.CharField(max_length=20)
    commentaire = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.paiement.eleve} | {self.montant}€ le {self.date} ({self.methode})"

    class Meta:
        verbose_name = "Historique de paiement"
        verbose_name_plural = "Historiques de paiements"


class ObjectifMensuel(models.Model):
    """Modèle pour les objectifs mensuels des élèves"""
    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('atteint', 'Atteint'),
        ('non_atteint', 'Non atteint'),
    ]
    
    eleve = models.ForeignKey('Eleve', on_delete=models.CASCADE, related_name='objectifs')
    mois = models.DateField(help_text="Mois et année de l'objectif")
    sourate = models.CharField(max_length=100, blank=True, null=True, help_text="Sourate ciblée")
    page_debut = models.PositiveIntegerField(blank=True, null=True, help_text="Page de début de la sourate")
    page_fin = models.PositiveIntegerField(blank=True, null=True, help_text="Page de fin de la sourate")
    numero_exercice = models.PositiveIntegerField(blank=True, null=True, help_text="Numéro d'exercice (1-13)")
    description_libre = models.TextField(blank=True, null=True, help_text="Description libre de l'objectif")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_cours')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    commentaire = models.TextField(blank=True, help_text="Commentaires sur l'objectif")
    
    def __str__(self):
        if self.sourate:
            return f"Objectif {self.eleve} - {self.sourate} ({self.get_statut_display()})"
        elif self.numero_exercice:
            return f"Objectif {self.eleve} - Exercice {self.numero_exercice} ({self.get_statut_display()})"
        else:
            return f"Objectif {self.eleve} - {self.mois.strftime('%B %Y')} ({self.get_statut_display()})"
    
    class Meta:
        verbose_name = "Objectif mensuel"
        verbose_name_plural = "Objectifs mensuels"
        ordering = ['-mois', 'eleve']


# Modèles pour les notes et évaluations

class NoteExamen(models.Model):
    """Modèle pour les notes d'examen des élèves"""
    TYPE_EXAMEN_CHOICES = [
        ('recitation', 'Récitation'),
        ('ecriture', 'Écriture'),
        ('tajwid', 'Tajwid'),
        ('comprehension', 'Compréhension'),
        ('quiz', 'Quiz en ligne'),
        ('autre', 'Autre'),
    ]
    
    eleve = models.ForeignKey('Eleve', on_delete=models.CASCADE, related_name='notes_examens')
    professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE, related_name='notes_donnees')
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, related_name='notes_examens')
    
    titre = models.CharField(max_length=200, help_text="Titre de l'examen (ex: Examen Sourate Al-Fatiha)")
    type_examen = models.CharField(max_length=20, choices=TYPE_EXAMEN_CHOICES, default='recitation')
    sourate_concernee = models.CharField(max_length=100, blank=True, null=True, help_text="Sourate concernée par l'examen")
    
    # Champs pour lier une note à un quiz
    # Utilisation de chaînes de caractères pour éviter les imports circulaires
    # Temporairement désactivés pour résoudre l'erreur
    # quiz = models.ForeignKey('ecole_app.quiz', on_delete=models.SET_NULL, null=True, blank=True, related_name='notes_examens')
    # tentative_quiz = models.ForeignKey('ecole_app.tentativequiz', on_delete=models.SET_NULL, null=True, blank=True, related_name='note_examen')
    
    note = models.DecimalField(max_digits=4, decimal_places=2, help_text="Note sur 20")
    note_max = models.DecimalField(max_digits=4, decimal_places=2, default=20, help_text="Note maximale")
    
    date_examen = models.DateField(help_text="Date de l'examen")
    commentaire = models.TextField(blank=True, help_text="Commentaires du professeur")
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.eleve} - {self.titre} - {self.note}/{self.note_max}"
    
    @property
    def pourcentage(self):
        """Calcule le pourcentage de la note"""
        if self.note_max > 0:
            return round((self.note / self.note_max) * 100, 1)
        return 0
    
    @property
    def mention(self):
        """Retourne la mention selon le pourcentage"""
        pourcentage = self.pourcentage
        if pourcentage >= 90:
            return "Excellent"
        elif pourcentage >= 80:
            return "Très bien"
        elif pourcentage >= 70:
            return "Bien"
        elif pourcentage >= 60:
            return "Assez bien"
        elif pourcentage >= 50:
            return "Passable"
        else:
            return "Insuffisant"
    
    @property
    def couleur_badge(self):
        """Retourne la couleur du badge selon la note"""
        pourcentage = self.pourcentage
        if pourcentage >= 80:
            return "success"
        elif pourcentage >= 60:
            return "warning"
        else:
            return "danger"
    
    class Meta:
        verbose_name = "Note d'examen"
        verbose_name_plural = "Notes d'examen"
        ordering = ['-date_examen', '-date_creation']


# Modèles pour les cours partagés et les quiz

class CoursPartage(models.Model):
    """Modèle pour les cours partagés par les professeurs"""
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    fichier = models.FileField(upload_to='cours_partages/')
    professeur = models.ForeignKey(Professeur, on_delete=models.CASCADE, related_name='cours_partages')
    eleve = models.ForeignKey('Eleve', on_delete=models.CASCADE, related_name='cours_partages', null=True, blank=True, help_text="Élève concerné (optionnel)")
    classes = models.ManyToManyField(Classe, related_name='cours_partages')
    # Champ date_debut avec valeur par défaut pour éviter les problèmes de migration
    date_debut = models.DateTimeField(default=timezone.now, help_text="Date de début du cours")
    date_creation = models.DateTimeField(default=timezone.now)
    date_modification = models.DateTimeField(auto_now=True)
    actif = models.BooleanField(default=True, help_text="Le cours est-il actif et visible ?")
    
    def __str__(self):
        return self.titre
    
    class Meta:
        verbose_name = "Cours partagé"
        verbose_name_plural = "Cours partagés"
        ordering = ['-date_creation']


class ProgressionCoran(models.Model):
    """Modèle pour suivre la progression de mémorisation du Coran par élève"""
    DIRECTION_CHOICES = [
        ('debut', 'Du début (Al-Baqara)'),
        ('fin', 'De la fin (An-Nas)'),
    ]
    
    eleve = models.OneToOneField('Eleve', on_delete=models.CASCADE, related_name='progression_coran')
    sourate_actuelle = models.CharField(max_length=100, blank=True, null=True, help_text="Sourate actuellement en cours de mémorisation")
    page_actuelle = models.PositiveIntegerField(default=1, help_text="Dernière page mémorisée")
    page_debut_sourate = models.PositiveIntegerField(default=1, help_text="Page de début de la sourate actuelle")
    direction_memorisation = models.CharField(max_length=10, choices=DIRECTION_CHOICES, default='debut', 
                                          help_text="Direction de mémorisation (du début ou de la fin du Coran)")
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Progression de {self.eleve} - Page {self.page_actuelle}"
    
    def calculer_pourcentage(self):
        """Calcule le pourcentage de progression basé sur la page actuelle et la direction de mémorisation"""
        total_pages = 604  # Nombre total de pages du Coran
        
        if self.direction_memorisation == 'debut':
            # Si mémorisation depuis le début (Al-Baqara)
            # Une page mémorisée = 1/604 = 0.17%
            return round((self.page_actuelle / total_pages) * 100, 2)
        else:
            # Si mémorisation depuis la fin (An-Nas)
            # Pour la mémorisation depuis la fin, on calcule:
            # 1. Les pages après la sourate actuelle (de la fin du Coran jusqu'à la sourate actuelle)
            # 2. Les pages dans la sourate actuelle (de la page actuelle jusqu'à la fin de la sourate)
            
            # Pages mémorisées après la sourate actuelle (toutes les pages après cette sourate)
            pages_apres_sourate = total_pages - self.page_debut_sourate
            
            # Pages mémorisées dans la sourate actuelle (de la page actuelle jusqu'à la fin de la sourate)
            # Plus la page_actuelle est grande, plus on a mémorisé de pages dans cette sourate
            pages_dans_sourate = self.page_actuelle - self.page_debut_sourate + 1
            
            # Total des pages mémorisées
            pages_memorisees = pages_apres_sourate + pages_dans_sourate
            
            return round((pages_memorisees / total_pages) * 100, 2)
    
    class Meta:
        verbose_name = "Progression du Coran"
        verbose_name_plural = "Progressions du Coran"

