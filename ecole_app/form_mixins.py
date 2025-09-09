from django import forms

class ComposanteFormMixin:
    """
    Mixin pour les formulaires qui doivent associer automatiquement
    les objets créés à la composante active dans la session.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialise le formulaire en récupérant la composante active depuis la requête.
        """
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
    def save(self, commit=True):
        """
        Sauvegarde le formulaire en associant l'objet à la composante active.
        """
        instance = super().save(commit=False)
        
        # Si une requête est disponible et qu'on a une composante en session
        if self.request and hasattr(self.request.session, 'get'):
            composante_id = self.request.session.get('composante_id')
            if composante_id:
                # Vérifier si l'instance a un champ composantes (ManyToMany) - cas du modèle Professeur
                if hasattr(instance, 'composantes'):
                    # Ne rien faire ici, car l'ajout à composantes se fait après la sauvegarde
                    pass
                # Vérifier si l'instance a un champ composante_id (ForeignKey) - cas des autres modèles
                elif hasattr(instance, 'composante_id') and not instance.composante_id:
                    instance.composante_id = composante_id
        
        if commit:
            instance.save()
            # N'appeler save_m2m que si l'instance a été sauvegardée
            if hasattr(self, 'save_m2m'):
                self.save_m2m()
        
        return instance
