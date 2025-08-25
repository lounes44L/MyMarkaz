from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve, reverse

class ComposanteMiddleware:
    """
    Middleware qui assure l'isolation des données par composante.
    - Vérifie si une composante est sélectionnée pour les URLs qui nécessitent une composante
    - Redirige vers la page de sélection de composante si nécessaire
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs qui ne nécessitent pas de composante active
        self.exempted_urls = [
            'login',
            'logout',
            'selection_composante',
            'changer_composante',
            'creer_composante',
            'modifier_composante',
            'supprimer_composante',
            'gestion_composantes',
            'statistiques_composante',
            'admin:',  # URLs d'administration Django
            'static',  # Fichiers statiques
            'media',   # Fichiers média
        ]
    
    def __call__(self, request):
        # Vérifier si l'URL actuelle nécessite une composante
        resolved = resolve(request.path_info)
        current_url = resolved.url_name
        
        # Si l'URL est exemptée ou current_url est None, on continue normalement
        if current_url is None or request.path.startswith('/admin/') or any(url in current_url for url in self.exempted_urls):
            return self.get_response(request)
        
        # Si l'utilisateur n'est pas connecté, on continue normalement (la vue login_required redirigera)
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Ne pas imposer la sélection de composante pour les élèves et les professeurs
        if (hasattr(request.user, 'eleve') and request.user.eleve) or (hasattr(request.user, 'professeur') and request.user.professeur):
            # Pour les professeurs, sélectionner automatiquement la première composante si aucune n'est sélectionnée
            if hasattr(request.user, 'professeur') and request.user.professeur and not request.session.get('composante_id'):
                if request.user.professeur.composantes.exists():
                    request.session['composante_id'] = request.user.professeur.composantes.first().id
            return self.get_response(request)

        # Vérifier si une composante est sélectionnée (pour les autres)
        composante_id = request.session.get('composante_id')
        if not composante_id:
            messages.warning(request, "Veuillez sélectionner une composante pour accéder à cette page.")
            return redirect('selection_composante')
        
        # Continuer avec la requête
        return self.get_response(request)
