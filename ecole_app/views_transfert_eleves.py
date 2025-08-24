from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Prefetch, Q
from .models import Classe, Eleve, Professeur, ObjectifMensuel
from .decorators import professeur_required

@login_required
@professeur_required
def liste_eleves_objectifs_nosidebar(request, classe_id):
    """
    Vue pour afficher la liste des élèves d'une classe avec leurs objectifs, sans la barre latérale
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
    
    # Récupérer toutes les classes des autres professeurs
    classes_autres_profs = Classe.objects.exclude(professeur=request.user.professeur).select_related('professeur')
    
    context = {
        'classe': classe,
        'eleves': eleves,
        'classes_autres_profs': classes_autres_profs,
    }
    
    return render(request, 'ecole_app/eleves/liste_eleves_objectifs_nosidebar.html', context)

@login_required
@professeur_required
def transferer_eleve(request, eleve_id):
    """
    Vue pour transférer un élève vers une autre classe
    """
    eleve = get_object_or_404(Eleve, id=eleve_id)
    
    # Vérifier que le professeur est bien le professeur de cet élève
    professeur = request.user.professeur
    classes_prof = Classe.objects.filter(professeur=professeur)
    
    if not (eleve.classe in classes_prof or eleve.classes.filter(id__in=classes_prof.values_list('id', flat=True)).exists()):
        messages.error(request, "Vous n'êtes pas autorisé à transférer cet élève.")
        return redirect('dashboard_professeur')
    
    if request.method == 'POST':
        classe_destination_id = request.POST.get('classe_destination')
        commentaire = request.POST.get('commentaire', '')
        conserver_copie = request.POST.get('conserver_copie', False) == 'on'
        
        classe_destination = get_object_or_404(Classe, id=classe_destination_id)
        
        # Effectuer le transfert
        if not conserver_copie:
            # Retirer l'élève de toutes les classes du professeur actuel
            if eleve.classe in classes_prof:
                eleve.classe = None
            
            eleve.classes.remove(*classes_prof.all())
        
        # Ajouter l'élève à la classe de destination
        eleve.classes.add(classe_destination)
        eleve.save()
        
        # Message de confirmation
        messages.success(
            request, 
            f"L'élève {eleve.prenom} {eleve.nom} a été transféré avec succès vers la classe {classe_destination.nom}."
        )
        
        # Rediriger vers la liste des élèves de la classe d'origine
        classe_origine_id = request.POST.get('classe_origine')
        if classe_origine_id:
            return redirect('liste_eleves_objectifs_nosidebar', classe_id=classe_origine_id)
        else:
            return redirect('dashboard_professeur')
    
    # Si la méthode n'est pas POST, rediriger vers le tableau de bord
    return redirect('dashboard_professeur')
