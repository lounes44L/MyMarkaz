from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Prefetch
from .models import Classe, Eleve, ObjectifMensuel, Composante
from .decorators import professeur_required, admin_required

@login_required
@professeur_required
def liste_eleves_objectifs(request, classe_id):
    """
    Vue pour afficher la liste des élèves d'une classe avec leurs informations personnelles et leurs objectifs
    """
    # Récupérer la classe
    classe = get_object_or_404(Classe, id=classe_id)
    
    # Vérifier que le professeur est bien le professeur de cette classe
    if request.user.professeur != classe.professeur:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette classe.")
        return redirect('dashboard_professeur')
    
    # Récupérer les élèves des deux relations (ForeignKey et ManyToMany)
    eleves_fk = Eleve.objects.filter(classe=classe, archive=False)
    eleves_m2m = Eleve.objects.filter(classes=classe, archive=False)
    
    # Fusionner les deux querysets sans doublons
    eleves = (eleves_fk | eleves_m2m).distinct().prefetch_related(
        Prefetch('objectifs', queryset=ObjectifMensuel.objects.order_by('-mois'))
    ).order_by('nom', 'prenom')
    
    # Récupérer les classes de la même composante pour le transfert
    classes_meme_composante = Classe.objects.filter(composante=classe.composante).exclude(id=classe.id).select_related('professeur')
    
    context = {
        'classe': classe,
        'eleves': eleves,
        'classes_meme_composante': classes_meme_composante,
    }
    
    return render(request, 'ecole_app/eleves/liste_eleves_objectifs.html', context)


@login_required
@admin_required
def admin_liste_eleves_objectifs(request, classe_id=None):
    """
    Vue pour permettre à l'administrateur d'accéder aux objectifs des élèves de n'importe quelle classe
    """
    # Si aucune classe n'est spécifiée, afficher la liste des classes
    if classe_id is None:
        # Récupérer la composante sélectionnée par l'admin
        from .views_composante import get_composante_courante
        composante_courante = get_composante_courante(request)
        
        if composante_courante:
            # Filtrer les classes par la composante sélectionnée
            classes = Classe.objects.filter(composante=composante_courante).order_by('nom')
        else:
            # Si aucune composante n'est sélectionnée, rediriger vers la sélection de composante
            from django.contrib import messages
            messages.info(request, 'Veuillez sélectionner une composante pour voir les objectifs des élèves.')
            return redirect('selection_composante')
            
        return render(request, 'ecole_app/eleves/admin_selection_classe.html', {'classes': classes})
    
    # Récupérer la classe
    classe = get_object_or_404(Classe, id=classe_id)
    
    # Récupérer les élèves des deux relations (ForeignKey et ManyToMany)
    eleves_fk = Eleve.objects.filter(classe=classe, archive=False)
    eleves_m2m = Eleve.objects.filter(classes=classe, archive=False)
    
    # Fusionner les deux querysets sans doublons
    eleves = (eleves_fk | eleves_m2m).distinct().prefetch_related(
        Prefetch('objectifs', queryset=ObjectifMensuel.objects.order_by('-mois'))
    ).order_by('nom', 'prenom')
    
    context = {
        'classe': classe,
        'eleves': eleves,
        'is_admin': True,
    }
    
    return render(request, 'ecole_app/eleves/liste_eleves_objectifs.html', context)
