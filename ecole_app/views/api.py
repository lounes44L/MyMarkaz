from django.http import JsonResponse
from django.views.decorators.http import require_GET
from ..sourate import get_pages_for_sourate, SOURATES

@require_GET
def get_sourate_pages(request):
    """API pour récupérer les pages d'une sourate spécifique"""
    sourate_index = request.GET.get('sourate_index')
    if sourate_index is None:
        return JsonResponse({'error': 'Paramètre sourate_index requis'}, status=400)
    
    try:
        # Convertir l'index en entier
        sourate_index = int(sourate_index)
        
        # Vérifier que l'index est valide
        if sourate_index < 0 or sourate_index >= len(SOURATES):
            return JsonResponse({
                'error': f'Index de sourate invalide: {sourate_index}. Doit être entre 0 et {len(SOURATES)-1}',
                'sourate_count': len(SOURATES)
            }, status=400)
        
        # Récupérer les pages
        pages = get_pages_for_sourate(sourate_index)
        
        # Vérifier qu'on a bien des pages
        if not pages:
            return JsonResponse({
                'error': f'Aucune page trouvée pour la sourate {sourate_index}',
                'sourate_info': {
                    'nom': SOURATES[sourate_index].nom,
                    'page_debut': SOURATES[sourate_index].page_debut,
                    'page_fin': SOURATES[sourate_index].page_fin
                }
            }, status=404)
        
        # Retourner les pages avec des informations supplémentaires pour le débogage
        return JsonResponse({
            'pages': pages,
            'sourate_info': {
                'nom': SOURATES[sourate_index].nom,
                'page_debut': SOURATES[sourate_index].page_debut,
                'page_fin': SOURATES[sourate_index].page_fin,
                'page_count': len(pages)
            }
        })
    except ValueError:
        return JsonResponse({'error': f'L\'index de sourate doit être un entier: {sourate_index}'}, status=400)
    except Exception as e:
        import traceback
        return JsonResponse({
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)

@require_GET
def find_sourate_by_page(request):
    """API pour trouver la sourate correspondant à une page ou plage de pages"""
    page = request.GET.get('page')
    debut_page = request.GET.get('debut_page')
    fin_page = request.GET.get('fin_page')
    
    # Si on a une seule page
    if page:
        try:
            page_num = int(page)
            for i, sourate in enumerate(SOURATES):
                if sourate.page_debut <= page_num <= sourate.page_fin:
                    return JsonResponse({
                        'sourate_index': i,
                        'sourate_nom': sourate.nom,
                        'page_debut': sourate.page_debut,
                        'page_fin': sourate.page_fin
                    })
            return JsonResponse({'error': 'Aucune sourate trouvée pour cette page'}, status=404)
        except ValueError:
            return JsonResponse({'error': 'Le numéro de page doit être un entier'}, status=400)
    
    # Si on a une plage de pages
    elif debut_page and fin_page:
        try:
            debut = int(debut_page)
            fin = int(fin_page)
            
            # On cherche la sourate qui contient à la fois la page de début et la page de fin
            for i, sourate in enumerate(SOURATES):
                if sourate.page_debut <= debut <= sourate.page_fin and sourate.page_debut <= fin <= sourate.page_fin:
                    return JsonResponse({
                        'sourate_index': i,
                        'sourate_nom': sourate.nom,
                        'page_debut': sourate.page_debut,
                        'page_fin': sourate.page_fin
                    })
            
            # Si on n'a pas trouvé, on retourne la sourate de la page de début
            for i, sourate in enumerate(SOURATES):
                if sourate.page_debut <= debut <= sourate.page_fin:
                    return JsonResponse({
                        'sourate_index': i,
                        'sourate_nom': sourate.nom,
                        'page_debut': sourate.page_debut,
                        'page_fin': sourate.page_fin,
                        'warning': 'La plage de pages s\'étend sur plusieurs sourates'
                    })
            
            return JsonResponse({'error': 'Aucune sourate trouvée pour cette plage de pages'}, status=404)
        except ValueError:
            return JsonResponse({'error': 'Les numéros de page doivent être des entiers'}, status=400)
    
    else:
        return JsonResponse({'error': 'Paramètres requis: soit page, soit debut_page ET fin_page'}, status=400)
