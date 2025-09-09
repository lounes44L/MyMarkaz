from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Module(models.Model):
    """Module pédagogique créé par un professeur"""
    composante = models.ForeignKey('ecole_app.Composante', on_delete=models.CASCADE, related_name='modules', null=True, blank=True)
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    professeur = models.ForeignKey('ecole_app.Professeur', on_delete=models.CASCADE, related_name='modules', null=True, blank=True)
    classes = models.ManyToManyField('ecole_app.Classe', related_name='modules', blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    publie = models.BooleanField(default=False, help_text="Module visible par les élèves")
    
    def __str__(self):
        return self.titre
    
    class Meta:
        verbose_name = "Module pédagogique"
        verbose_name_plural = "Modules pédagogiques"
        ordering = ['-date_creation']

class Document(models.Model):
    """Document PDF associé à un module"""
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='documents')
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    fichier = models.FileField(upload_to='documents/%Y/%m/')
    date_creation = models.DateTimeField(auto_now_add=True)
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    
    def __str__(self):
        return self.titre
    
    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['ordre', 'date_creation']

class Quiz(models.Model):
    """Quiz associé à un module"""
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='quiz')
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    publie = models.BooleanField(default=False, help_text="Quiz visible par les élèves")
    temps_limite = models.PositiveIntegerField(null=True, blank=True, help_text="Temps limite en minutes (optionnel)")
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    
    def __str__(self):
        return self.titre
    
    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quiz"
        ordering = ['ordre', 'date_creation']

class Question(models.Model):
    """Question d'un quiz"""
    TYPES = [
        ('choix_unique', 'Choix unique'),
        ('choix_multiple', 'Choix multiple'),
        ('texte_court', 'Réponse texte courte'),
        ('vrai_faux', 'Vrai ou Faux'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    texte = models.TextField()
    type = models.CharField(max_length=20, choices=TYPES, default='choix_unique')
    points = models.PositiveIntegerField(default=1, help_text="Nombre de points pour cette question")
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    
    def __str__(self):
        return f"{self.texte[:50]}..."
    
    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['ordre']

class Choix(models.Model):
    """Choix possible pour une question"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choix')
    texte = models.CharField(max_length=255)
    est_correct = models.BooleanField(default=False)
    ordre = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    
    def __str__(self):
        return self.texte
    
    class Meta:
        verbose_name = "Choix"
        verbose_name_plural = "Choix"
        ordering = ['ordre']

class TentativeQuiz(models.Model):
    """Tentative d'un élève pour un quiz"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='tentatives')
    eleve = models.ForeignKey('ecole_app.Eleve', on_delete=models.CASCADE, related_name='tentatives_quiz')
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    terminee = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.eleve} - {self.quiz} ({self.date_debut.strftime('%d/%m/%Y')})"
    
    class Meta:
        verbose_name = "Tentative de quiz"
        verbose_name_plural = "Tentatives de quiz"
        ordering = ['-date_debut']
        
    def calculer_score(self):
        """Calcule le score de la tentative"""
        if not self.terminee:
            return None
            
        total_points = sum(q.points for q in self.quiz.questions.all())
        if total_points == 0:
            return 0
            
        points_obtenus = 0
        for reponse in self.reponses.all():
            if reponse.est_correcte:
                points_obtenus += reponse.question.points
                
        return (points_obtenus / total_points) * 100

class Reponse(models.Model):
    """Réponse d'un élève à une question"""
    tentative = models.ForeignKey(TentativeQuiz, on_delete=models.CASCADE, related_name='reponses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choix_selectionnes = models.ManyToManyField(Choix, blank=True, related_name='reponses')
    texte_reponse = models.TextField(blank=True, null=True)
    est_correcte = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Réponse à {self.question}"
    
    def verifier_reponse(self):
        """Vérifie si la réponse est correcte"""
        # Vérifier si l'objet a un ID avant d'accéder à la relation ManyToMany
        if not self.pk:
            return False
            
        if self.question.type == 'texte_court':
            # Pour les réponses textuelles, on compare avec les réponses correctes (à implémenter)
            return False
        elif self.question.type == 'vrai_faux':
            # Pour vrai/faux, on vérifie si le choix sélectionné est correct
            try:
                if self.choix_selectionnes.count() == 1:
                    return self.choix_selectionnes.first().est_correct
                return False
            except Exception:
                return False
        elif self.question.type == 'choix_unique':
            # Pour choix unique, on vérifie si le choix sélectionné est correct
            try:
                if self.choix_selectionnes.count() == 1:
                    return self.choix_selectionnes.first().est_correct
                return False
            except Exception:
                return False
        elif self.question.type == 'choix_multiple':
            # Pour choix multiple, tous les choix corrects doivent être sélectionnés
            # et aucun choix incorrect ne doit être sélectionné
            try:
                choix_corrects = self.question.choix.filter(est_correct=True)
                choix_selectionnes = self.choix_selectionnes.all()
                
                if choix_corrects.count() != choix_selectionnes.filter(est_correct=True).count():
                    return False
                    
                if choix_selectionnes.filter(est_correct=False).exists():
                    return False
                    
                return True
            except Exception:
                return False
        
        return False
    
    def save(self, *args, **kwargs):
        # Sauvegarder d'abord l'objet pour qu'il ait un ID
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Vérifier si la réponse est correcte seulement après avoir sauvegardé
        # et uniquement si des choix ont été ajoutés (pas lors de la création initiale)
        if not is_new:
            est_correcte = self.verifier_reponse()
            if self.est_correcte != est_correcte:
                self.est_correcte = est_correcte
                # Éviter une récursion infinie en utilisant update
                type(self).objects.filter(pk=self.pk).update(est_correcte=est_correcte)
