from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Count
from datetime import datetime, timedelta
from django.views.decorators.http import require_POST
from .models import Classe, Eleve, Professeur, PresenceEleve, PresenceProfesseur, AnneeScolaire
from .forms import PresenceEleveForm, PresenceProfesseurForm, PresenceMultipleForm
from .views_auth import is_admin, is_professeur

@login_required
def liste_presences_eleves(request):
    """Vue pour afficher la liste des prÃ©sences des Ã©lÃ¨ves"""
    # Obtenir l'annÃ©e scolaire active
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    
    # RÃ©cupÃ©rer toutes les prÃ©sences des Ã©lÃ¨ves
    presences = PresenceEleve.objects.select_related('eleve', 'classe')
    # Note: Le modÃ¨le PresenceEleve n'a pas de champ annee_scolaire, donc on ne filtre pas par annÃ©e
    
    # Tri par date, les plus rÃ©centes en premier
    presences = presences.order_by('-date')
    
    # Compter les prÃ©sences par Ã©lÃ¨ve
    presences_par_eleve = presences.values('eleve__id', 'eleve__nom', 'eleve__prenom').annotate(
        count_present=Count('id', filter=Q(present=True)),
        count_absent=Count('id', filter=Q(present=False))
    )
    
    context = {
        'presences': presences,
        'presences_par_eleve': presences_par_eleve,
        'annee_active': annee_active,
    }
    return render(request, 'ecole_app/presences/liste_eleves.html', context)

@login_required
def liste_presences_professeurs(request):
    """Vue pour afficher la liste des prÃ©sences des professeurs"""
    # Obtenir l'annÃ©e scolaire active
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    
    # RÃ©cupÃ©rer toutes les prÃ©sences des professeurs
    presences = PresenceProfesseur.objects.select_related('professeur')
    # Note: Le modÃ¨le PresenceProfesseur n'a pas de champ annee_scolaire, donc on ne filtre pas par annÃ©e
    
    # Tri par date, les plus rÃ©centes en premier
    presences = presences.order_by('-date')
    
    # Compter les prÃ©sences par professeur
    presences_par_professeur = presences.values('professeur__id', 'professeur__nom').annotate(
        count_present=Count('id', filter=Q(present=True)),
        count_absent=Count('id', filter=Q(present=False))
    )
    
    context = {
        'presences': presences,
        'presences_par_professeur': presences_par_professeur,
        'annee_active': annee_active,
    }
    return render(request, 'ecole_app/presences/liste_professeurs.html', context)

@login_required
def presences_classe(request, classe_id):
    """Vue pour gÃ©rer les prÃ©sences des Ã©lÃ¨ves d'une classe spÃ©cifique"""
    classe = get_object_or_404(Classe, pk=classe_id)
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    
    # VÃ©rifier si l'utilisateur est un professeur et s'il est bien assignÃ© Ã  cette classe
    if is_professeur(request.user) and not is_admin(request.user):
        if request.user.professeur != classe.professeur:
            messages.error(request, "Vous n'avez pas accÃ¨s Ã  cette classe.")
            return redirect('dashboard_professeur')
    
    # RÃ©cupÃ©rer tous les Ã©lÃ¨ves de la classe (ForeignKey et ManyToMany)
    eleves_fk = classe.eleves.filter(archive=False)
    eleves_m2m = classe.eleves_multi.filter(archive=False)
    eleves = (eleves_fk | eleves_m2m).distinct().order_by('nom', 'prenom')
    
    if request.method == 'POST':
        # Formulaire pour plusieurs Ã©lÃ¨ves Ã  la fois
        form = PresenceMultipleForm(request.POST)
        if form.is_valid():
            date_presence = form.cleaned_data['date']
            commentaire = form.cleaned_data['commentaire']
            
            # Parcourir tous les Ã©lÃ¨ves pour lesquels une prÃ©sence a Ã©tÃ© soumise
            presences_creees = 0
            for eleve in eleves:
                present_key = f'present_{eleve.id}'
                if present_key in request.POST:
                    present = request.POST.get(present_key) == 'on'
                    
                    # VÃ©rifier si une prÃ©sence existe dÃ©jÃ  pour cette date et cet Ã©lÃ¨ve
                    presence_existante = PresenceEleve.objects.filter(
                        eleve=eleve,
                        date=date_presence,
                        classe=classe
                    ).first()
                    
                    if presence_existante:
                        # Mettre Ã  jour la prÃ©sence existante
                        presence_existante.present = present
                        presence_existante.commentaire = commentaire
                        presence_existante.save()
                    else:
                        # CrÃ©er une nouvelle prÃ©sence
                        PresenceEleve.objects.create(
                            eleve=eleve,
                            date=date_presence,
                            present=present,
                            classe=classe,
                            commentaire=commentaire,
                            annee_scolaire=annee_active
                        )
                    presences_creees += 1
            
            messages.success(request, f"{presences_creees} prÃ©sence(s) enregistrÃ©e(s) avec succÃ¨s.")
            return redirect('presences_classe', classe_id=classe.id)
    else:
        form = PresenceMultipleForm(initial={'date': timezone.now().date()})
    
    # RÃ©cupÃ©rer l'historique des prÃ©sences pour cette classe
    historique = PresenceEleve.objects.filter(classe=classe).order_by('-date')
    # Suppression du filtre annee_scolaire car ce champ n'existe pas sur PresenceEleve
    
    context = {
        'classe': classe,
        'eleves': eleves,
        'form': form,
        'historique': historique,
        'annee_active': annee_active,
    }
    return render(request, 'ecole_app/presences/classe.html', context)

@login_required
def presences_eleve(request, eleve_id):
    """Vue pour consulter les prÃ©sences d'un Ã©lÃ¨ve spÃ©cifique"""
    eleve = get_object_or_404(Eleve.objects.prefetch_related('classes'), pk=eleve_id)
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    
    # RÃ©cupÃ©rer toutes les classes de l'Ã©lÃ¨ve
    classes_eleve = eleve.classes.all()
    
    # Si l'utilisateur est l'Ã©lÃ¨ve lui-mÃªme, il peut voir ses propres prÃ©sences
    est_autorise = (is_admin(request.user) or 
                   (is_professeur(request.user) and any(request.user.professeur == classe.professeur for classe in classes_eleve)) or
                   (hasattr(request.user, 'eleve') and request.user.eleve == eleve))
    
    if not est_autorise:
        messages.error(request, "Vous n'avez pas accÃ¨s aux prÃ©sences de cet Ã©lÃ¨ve.")
        return redirect('dashboard')
    
    # Filtrer par classe si spÃ©cifiÃ© dans l'URL
    classe_id = request.GET.get('classe')
    classe_selectionnee = None
    
    if classe_id:
        try:
            classe_selectionnee = classes_eleve.get(id=classe_id)
            presences = PresenceEleve.objects.filter(eleve=eleve, classe=classe_selectionnee).order_by('-date')
        except:
            presences = PresenceEleve.objects.filter(eleve=eleve).order_by('-date')
    else:
        # RÃ©cupÃ©rer toutes les prÃ©sences de l'Ã©lÃ¨ve pour toutes ses classes
        presences = PresenceEleve.objects.filter(eleve=eleve).order_by('-date')
    
    # Statistiques
    total_presences = presences.filter(present=True).count()
    total_absences = presences.filter(present=False).count()
    total = total_presences + total_absences
    taux_presence = (total_presences / total * 100) if total > 0 else 0
    
    context = {
        'eleve': eleve,
        'classes': classes_eleve,
        'classe_selectionnee': classe_selectionnee,
        'presences': presences,
        'total_presences': total_presences,
        'total_absences': total_absences,
        'taux_presence': taux_presence,
        'annee_active': annee_active,
    }
    return render(request, 'ecole_app/presences/eleve.html', context)

@login_required
@user_passes_test(is_admin)
def ajouter_presence_eleve(request):
    """Vue pour ajouter une prÃ©sence individuelle pour un Ã©lÃ¨ve"""
    if request.method == 'POST':
        form = PresenceEleveForm(request.POST)
        if form.is_valid():
            presence = form.save(commit=False)
            annee_active = AnneeScolaire.objects.filter(active=True).first()
            presence.annee_scolaire = annee_active
            presence.save()
            messages.success(request, "PrÃ©sence enregistrÃ©e avec succÃ¨s.")
            return redirect('liste_presences_eleves')
    else:
        form = PresenceEleveForm()
    
    context = {
        'form': form,
        'titre': "Ajouter une prÃ©sence pour un Ã©lÃ¨ve",
        'submit_text': "Enregistrer",
    }
    return render(request, 'ecole_app/presences/formulaire_eleve.html', context)

@login_required
def modifier_presence_eleve(request, presence_id):
    """Vue pour modifier une prÃ©sence d'un Ã©lÃ¨ve"""
    presence = get_object_or_404(PresenceEleve, pk=presence_id)
    
    # VÃ©rifier si l'utilisateur est autorisÃ© Ã  modifier cette prÃ©sence
    est_admin_user = is_admin(request.user)
    est_prof_classe = False
    
    if hasattr(request.user, 'professeur'):
        # VÃ©rifier si le professeur enseigne dans la classe de l'Ã©lÃ¨ve
        if presence.classe:
            est_prof_classe = presence.classe in request.user.professeur.get_all_classes()
    
    if not (est_admin_user or est_prof_classe):
        messages.error(request, "Vous n'Ãªtes pas autorisÃ© Ã  modifier cette prÃ©sence.")
        return redirect('rapport_presence_eleve')
    
    if request.method == 'POST':
        form = PresenceEleveForm(request.POST, instance=presence)
        if form.is_valid():
            # RÃ©cupÃ©rer le statut sÃ©lectionnÃ©
            status = request.POST.get('status')
            
            # Mettre Ã  jour les champs present et justifie en fonction du statut
            if status == 'present':
                form.instance.present = True
                form.instance.justifie = False
            elif status == 'absent_justifie':
                form.instance.present = False
                form.instance.justifie = True
            elif status == 'absent':
                form.instance.present = False
                form.instance.justifie = False
                
            form.save()
            messages.success(request, "PrÃ©sence modifiÃ©e avec succÃ¨s.")
            # Rediriger vers le rapport de prÃ©sence au lieu de la liste
            return redirect('rapport_presence_eleve')
    else:
        form = PresenceEleveForm(instance=presence)
    
    context = {
        'form': form,
        'titre': "Modifier une prÃ©sence",
        'submit_text': "Mettre Ã  jour",
        'presence': presence,
    }
    return render(request, 'ecole_app/presences/formulaire_eleve.html', context)

@login_required
def supprimer_presence_eleve(request, presence_id):
    """Vue pour supprimer une prÃ©sence d'un Ã©lÃ¨ve"""
    presence = get_object_or_404(PresenceEleve, pk=presence_id)
    
    # VÃ©rifier si l'utilisateur est autorisÃ© Ã  supprimer cette prÃ©sence
    est_admin_user = is_admin(request.user)
    est_prof_classe = False
    
    if hasattr(request.user, 'professeur'):
        # VÃ©rifier si le professeur enseigne dans la classe de l'Ã©lÃ¨ve
        if presence.classe:
            est_prof_classe = presence.classe in request.user.professeur.get_all_classes()
    
    if not (est_admin_user or est_prof_classe):
        messages.error(request, "Vous n'Ãªtes pas autorisÃ© Ã  supprimer cette prÃ©sence.")
        return redirect('rapport_presence_eleve')
    
    if request.method == 'POST':
        presence.delete()
        messages.success(request, "PrÃ©sence supprimÃ©e avec succÃ¨s.")
        # Rediriger vers le rapport de prÃ©sence au lieu de la liste
        return redirect('rapport_presence_eleve')
    
    context = {
        'presence': presence,
        'type_objet': 'la prÃ©sence',
    }
    return render(request, 'ecole_app/confirmation_suppression.html', context)

@login_required
@user_passes_test(is_admin)
def ajouter_presence_professeur(request):
    """Vue pour ajouter une prÃ©sence pour un professeur"""
    if request.method == 'POST':
        form = PresenceProfesseurForm(request.POST)
        if form.is_valid():
            presence = form.save(commit=False)
            annee_active = AnneeScolaire.objects.filter(active=True).first()
            presence.annee_scolaire = annee_active
            presence.save()
            messages.success(request, "PrÃ©sence enregistrÃ©e avec succÃ¨s.")
            return redirect('rapport_presence_professeur')
    else:
        form = PresenceProfesseurForm()
    
    context = {
        'form': form,
        'titre': "Ajouter une prÃ©sence pour un professeur",
        'submit_text': "Enregistrer",
    }
    return render(request, 'ecole_app/presences/formulaire_professeur.html', context)

@login_required
@user_passes_test(is_admin)
def modifier_presence_professeur(request, presence_id):
    """Vue pour modifier une prÃ©sence d'un professeur"""
    presence = get_object_or_404(PresenceProfesseur, pk=presence_id)
    
    if request.method == 'POST':
        form = PresenceProfesseurForm(request.POST, instance=presence)
        if form.is_valid():
            form.save()
            messages.success(request, "PrÃ©sence modifiÃ©e avec succÃ¨s.")
            return redirect('rapport_presence_professeur')
    else:
        form = PresenceProfesseurForm(instance=presence)
    
    context = {
        'form': form,
        'titre': "Modifier une prÃ©sence",
        'submit_text': "Mettre Ã  jour",
        'presence': presence,
    }
    return render(request, 'ecole_app/presences/formulaire_professeur.html', context)

@login_required
@user_passes_test(is_admin)
def supprimer_presence_professeur(request, presence_id):
    """Vue pour supprimer une prÃ©sence d'un professeur"""
    presence = get_object_or_404(PresenceProfesseur, pk=presence_id)
    
    if request.method == 'POST':
        presence.delete()
        messages.success(request, "PrÃ©sence supprimÃ©e avec succÃ¨s.")
        return redirect('rapport_presence_professeur')
    
    context = {
        'presence': presence,
        'type_objet': 'la prÃ©sence',
    }
    return render(request, 'ecole_app/confirmation_suppression.html', context)

@login_required
@require_POST
def modifier_presence_eleve_ajax(request):
    """Vue AJAX pour modifier une prÃ©sence d'Ã©lÃ¨ve sans redirection"""
    presence_id = request.POST.get('presence_id')
    status = request.POST.get('status')
    commentaire = request.POST.get('commentaire')
    
    if not presence_id or not status:
        return JsonResponse({'success': False, 'message': 'Données incomplètes'}, status=400)
    
    try:
        presence = get_object_or_404(PresenceEleve, pk=presence_id)
        
        # VÃ©rifier si l'utilisateur est autorisÃ© Ã  modifier cette prÃ©sence
        est_admin_user = is_admin(request.user)
        est_prof_classe = False
        
        if hasattr(request.user, 'professeur'):
            # VÃ©rifier si le professeur enseigne dans la classe de l'Ã©lÃ¨ve
            if presence.classe:
                est_prof_classe = presence.classe in request.user.professeur.get_all_classes()
        
        if not (est_admin_user or est_prof_classe):
            return JsonResponse({'success': False, 'message': 'Non autorisé'}, status=403)
        
        # Mettre Ã  jour les champs present et justifie en fonction du statut
        if status == 'present':
            presence.present = True
            presence.justifie = False
        elif status == 'absent_justifie':
            presence.present = False
            presence.justifie = True
        elif status == 'absent':
            presence.present = False
            presence.justifie = False
        else:
            return JsonResponse({'success': False, 'message': 'Statut invalide'}, status=400)
        
        # Mettre Ã  jour le commentaire
        presence.commentaire = commentaire
        presence.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Présence modifiée avec succès',
            'status': status,
            'commentaire': commentaire or '-'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)