from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden

def eleve_required(view_func):
    """
    Décorateur qui vérifie si l'utilisateur connecté est un élève.
    Redirige vers la page de connexion si l'utilisateur n'est pas connecté,
    ou renvoie une erreur 403 si l'utilisateur n'est pas un élève.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'eleve') or request.user.eleve is None:
            return HttpResponseForbidden("Vous devez être un élève pour accéder à cette page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def professeur_required(view_func):
    """
    Décorateur qui vérifie si l'utilisateur connecté est un professeur.
    Redirige vers la page de connexion si l'utilisateur n'est pas connecté,
    ou renvoie une erreur 403 si l'utilisateur n'est pas un professeur.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'professeur') or request.user.professeur is None:
            return HttpResponseForbidden("Vous devez être un professeur pour accéder à cette page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    """
    Décorateur qui vérifie si l'utilisateur connecté est un administrateur.
    Redirige vers la page de connexion si l'utilisateur n'est pas connecté,
    ou renvoie une erreur 403 si l'utilisateur n'est pas un administrateur.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_staff or request.user.is_superuser):
            return HttpResponseForbidden("Vous devez être un administrateur pour accéder à cette page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
