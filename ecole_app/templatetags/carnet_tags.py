from django import template
from ..sourate import SOURATES

register = template.Library()

@register.filter
def get_sourate_from_pages(page_debut, page_fin):
    """
    Détermine la sourate à partir des pages de début et fin
    """
    if not page_debut or not page_fin:
        return "-"
    
    # Rechercher la sourate correspondant à la page de début
    for sourate in SOURATES:
        if sourate.page_debut <= page_debut <= sourate.page_fin:
            return sourate.nom
    
    return "-"

@register.filter
def get_sourate_for_memo(memo):
    """
    Détermine la sourate pour une mémorisation
    """
    if not memo:
        return "-"
    
    return get_sourate_from_pages(memo.debut_page, memo.fin_page)
