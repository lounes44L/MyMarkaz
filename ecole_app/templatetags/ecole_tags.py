from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def dashboard_url(context):
    """
    Retourne l'URL du tableau de bord approprié selon le type d'utilisateur connecté.
    """
    user = context['request'].user
    
    if not user.is_authenticated:
        return reverse('login')
    
    if hasattr(user, 'professeur') and user.professeur:
        return reverse('dashboard_professeur')
    
    if hasattr(user, 'eleve') and user.eleve:
        return reverse('dashboard_eleve')
    
    # Par défaut pour admin/staff
    return reverse('dashboard')
