from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Count
from datetime import datetime, timedelta
from .models import Classe, Eleve, Professeur, PresenceEleve, PresenceProfesseur, AnneeScolaire
from .forms import PresenceEleveForm, PresenceProfesseurForm, PresenceMultipleForm
from .views_auth import is_admin, is_professeur

@login_required
def liste_presences_eleves(request):
    """Vue pour afficher la liste des présences des élèves"""
    # Obtenir l'année scolaire active
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    
    # Récupérer toutes les présences des élèves
    presences = PresenceEleve.objects.select_related('eleve', 'classe')
    # Note: Le modèle PresenceEleve n'a pas de champ annee_scolaire, donc on ne filtre pas par année
    
    # Tri par date, les plus récentes en premier
    presences = presences.order_by('-date')
    
    # Compter les présences par élève
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
    """Vue pour afficher la liste des présences des professeurs"""
    # Obtenir l'année scolaire active
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    
    # Récupérer toutes les présences des professeurs
    presences = PresenceProfesseur.objects.select_related('professeur')
    # Note: Le modèle PresenceProfesseur n'a pas de champ annee_scolaire, donc on ne filtre pas par année
    
    # Tri par date, les plus récentes en premier
    presences = presences.order_by('-date')
    
    # Compter les présences par professeur
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
    """Vue pour gérer les présences des élèves d'une classe spécifique"""
    classe = get_object_or_404(Classe, pk=classe_id)
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    
    # Vérifier si l'utilisateur est un professeur et s'il est bien assigné à cette classe
    if is_professeur(request.user) and not is_admin(request.user):
        if request.user.professeur != classe.professeur:
            messages.error(request, "Vous n'avez pas accès à cette classe.")
            return redirect('dashboard_professeur')
    
    # Récupérer tous les élèves de la classe (ForeignKey et ManyToMany)
    eleves_fk = classe.eleves.filter(archive=False)
    eleves_m2m = classe.eleves_multi.filter(archive=False)
    eleves = (eleves_fk | eleves_m2m).distinct().order_by('nom', 'prenom')
    
    if request.method == 'POST':
        # Formulaire pour plusieurs élèves à la fois
        form = PresenceMultipleForm(request.POST)
        if form.is_valid():
            date_presence = form.cleaned_data['date']
            commentaire = form.cleaned_data['commentaire']
            
            # Parcourir tous les élèves pour lesquels une présence a été soumise
            presences_creees = 0
            for eleve in eleves:
                present_key = f'present_{eleve.id}'
                if present_key in request.POST:
                    present = request.POST.get(present_key) == 'on'
                    
                    # Vérifier si une présence existe déjà pour cette date et cet élève
                    presence_existante = PresenceEleve.objects.filter(
                        eleve=eleve,
                        date=date_presence,
                        classe=classe
                    ).first()
                    
                    if presence_existante:
                        # Mettre à jour la présence existante
                        presence_existante.present = present
                        presence_existante.commentaire = commentaire
                        presence_existante.save()
                    else:
                        # Créer une nouvelle présence
                        PresenceEleve.objects.create(
                            eleve=eleve,
                            date=date_presence,
                            present=present,
                            classe=classe,
                            commentaire=commentaire,
                            annee_scolaire=annee_active
                        )
                    presences_creees += 1
            
            messages.success(request, f"{presences_creees} présence(s) enregistrée(s) avec succès.")
            return redirect('presences_classe', classe_id=classe.id)
    else:
        form = PresenceMultipleForm(initial={'date': timezone.now().date()})
    
    # Récupérer l'historique des présences pour cette classe
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
    """Vue pour consulter les présences d'un élève spécifique"""
    eleve = get_object_or_404(Eleve.objects.prefetch_related('classes'), pk=eleve_id)
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    
    # Récupérer toutes les classes de l'élève
    classes_eleve = eleve.classes.all()
    
    # Si l'utilisateur est l'élève lui-même, il peut voir ses propres présences
    est_autorise = (is_admin(request.user) or 
                   (is_professeur(request.user) and any(request.user.professeur == classe.professeur for classe in classes_eleve)) or
                   (hasattr(request.user, 'eleve') and request.user.eleve == eleve))
    
    if not est_autorise:
        messages.error(request, "Vous n'avez pas accès aux présences de cet élève.")
        return redirect('dashboard')
    
    # Filtrer par classe si spécifié dans l'URL
    classe_id = request.GET.get('classe')
    classe_selectionnee = None
    
    if classe_id:
        try:
            classe_selectionnee = classes_eleve.get(id=classe_id)
            presences = PresenceEleve.objects.filter(eleve=eleve, classe=classe_selectionnee).order_by('-date')
        except:
            presences = PresenceEleve.objects.filter(eleve=eleve).order_by('-date')
    else:
        # Récupérer toutes les présences de l'élève pour toutes ses classes
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
    """Vue pour ajouter une présence individuelle pour un élève"""
    if request.method == 'POST':
        form = PresenceEleveForm(request.POST)
        if form.is_valid():
            presence = form.save(commit=False)
            annee_active = AnneeScolaire.objects.filter(active=True).first()
            presence.annee_scolaire = annee_active
            presence.save()
            messages.success(request, "Présence enregistrée avec succès.")
            return redirect('liste_presences_eleves')
    else:
        form = PresenceEleveForm()
    
    context = {
        'form': form,
        'titre': "Ajouter une présence pour un élève",
        'submit_text': "Enregistrer",
    }
    return render(request, 'ecole_app/presences/formulaire_eleve.html', context)

@login_required
def modifier_presence_eleve(request, presence_id):
    """Vue pour modifier une présence d'un élève"""
    presence = get_object_or_404(PresenceEleve, pk=presence_id)
    
    # Vérifier si l'utilisateur est autorisé à modifier cette présence
    est_admin_user = is_admin(request.user)
    est_prof_classe = False
    
    if hasattr(request.user, 'professeur'):
        # Vérifier si le professeur enseigne dans la classe de l'élève
        if presence.classe:
            est_prof_classe = presence.classe in request.user.professeur.get_all_classes()
    
    if not (est_admin_user or est_prof_classe):
        messages.error(request, "Vous n'êtes pas autorisé à modifier cette présence.")
        return redirect('rapport_presence_eleve')
    
    if request.method == 'POST':
        form = PresenceEleveForm(request.POST, instance=presence)
        if form.is_valid():
            form.save()
            messages.success(request, "Présence modifiée avec succès.")
            # Rediriger vers le rapport de présence au lieu de la liste
            return redirect('rapport_presence_eleve')
    else:
        form = PresenceEleveForm(instance=presence)
    
    context = {
        'form': form,
        'titre': "Modifier une présence",
        'submit_text': "Mettre à jour",
        'presence': presence,
    }
    return render(request, 'ecole_app/presences/formulaire_eleve.html', context)

@login_required
def supprimer_presence_eleve(request, presence_id):
    """Vue pour supprimer une présence d'un élève"""
    presence = get_object_or_404(PresenceEleve, pk=presence_id)
    
    # Vérifier si l'utilisateur est autorisé à supprimer cette présence
    est_admin_user = is_admin(request.user)
    est_prof_classe = False
    
    if hasattr(request.user, 'professeur'):
        # Vérifier si le professeur enseigne dans la classe de l'élève
        if presence.classe:
            est_prof_classe = presence.classe in request.user.professeur.get_all_classes()
    
    if not (est_admin_user or est_prof_classe):
        messages.error(request, "Vous n'êtes pas autorisé à supprimer cette présence.")
        return redirect('rapport_presence_eleve')
    
    if request.method == 'POST':
        presence.delete()
        messages.success(request, "Présence supprimée avec succès.")
        # Rediriger vers le rapport de présence au lieu de la liste
        return redirect('rapport_presence_eleve')
    
    context = {
        'presence': presence,
        'type_objet': 'la présence',
    }
    return render(request, 'ecole_app/confirmation_suppression.html', context)

@login_required
@user_passes_test(is_admin)
def ajouter_presence_professeur(request):
    """Vue pour ajouter une présence pour un professeur"""
    if request.method == 'POST':
        form = PresenceProfesseurForm(request.POST)
        if form.is_valid():
            presence = form.save(commit=False)
            annee_active = AnneeScolaire.objects.filter(active=True).first()
            presence.annee_scolaire = annee_active
            presence.save()
            messages.success(request, "Présence enregistrée avec succès.")
            return redirect('rapport_presence_professeur')
    else:
        form = PresenceProfesseurForm()
    
    context = {
        'form': form,
        'titre': "Ajouter une présence pour un professeur",
        'submit_text': "Enregistrer",
    }
    return render(request, 'ecole_app/presences/formulaire_professeur.html', context)

@login_required
@user_passes_test(is_admin)
def modifier_presence_professeur(request, presence_id):
    """Vue pour modifier une présence d'un professeur"""
    presence = get_object_or_404(PresenceProfesseur, pk=presence_id)
    
    if request.method == 'POST':
        form = PresenceProfesseurForm(request.POST, instance=presence)
        if form.is_valid():
            form.save()
            messages.success(request, "Présence modifiée avec succès.")
            return redirect('rapport_presence_professeur')
    else:
        form = PresenceProfesseurForm(instance=presence)
    
    context = {
        'form': form,
        'titre': "Modifier une présence",
        'submit_text': "Mettre à jour",
        'presence': presence,
    }
    return render(request, 'ecole_app/presences/formulaire_professeur.html', context)

@login_required
@user_passes_test(is_admin)
def supprimer_presence_professeur(request, presence_id):
    """Vue pour supprimer une présence d'un professeur"""
    presence = get_object_or_404(PresenceProfesseur, pk=presence_id)
    
    if request.method == 'POST':
        presence.delete()
        messages.success(request, "Présence supprimée avec succès.")
        return redirect('rapport_presence_professeur')
    
    context = {
        'presence': presence,
        'type_objet': 'la présence',
    }
    return render(request, 'ecole_app/confirmation_suppression.html', context)
