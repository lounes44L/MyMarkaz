from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponse
from .models import Professeur, PresenceProfesseur, Creneau, AnneeScolaire
import datetime
from django.utils import timezone

@login_required
def gestion_presence_professeur(request):
    """Vue pour gérer les présences des professeurs"""
    # Récupérer TOUS les professeurs sans filtre
    tous_les_professeurs = Professeur.objects.all().order_by('nom')
    
    # Récupérer la date sélectionnée ou utiliser la date du jour
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()
    
    # Récupérer les créneaux disponibles
    creneaux = Creneau.objects.all().order_by('heure_debut')
    
    # Récupérer le créneau sélectionné ou utiliser le premier créneau
    creneau_id = request.GET.get('creneau')
    selected_creneau = None
    if creneau_id:
        try:
            selected_creneau = Creneau.objects.get(id=creneau_id)
        except Creneau.DoesNotExist:
            if creneaux.exists():
                selected_creneau = creneaux.first()
    elif creneaux.exists():
        selected_creneau = creneaux.first()
    
    # Traitement du formulaire de présence
    if request.method == 'POST':
        professeur_id = request.POST.get('professeur_id')
        status = request.POST.get('status')
        commentaire = request.POST.get('commentaire', '')
        date = request.POST.get('date')
        creneau_id = request.POST.get('creneau_id')
        
        # Gestion des statuts
        present = False
        if status == 'present':
            present = True
        elif status == 'absent':
            present = False
        
        if professeur_id and date:
            try:
                professeur = Professeur.objects.get(id=professeur_id)
                date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
                creneau = None
                if creneau_id:
                    try:
                        creneau = Creneau.objects.get(id=creneau_id)
                    except Creneau.DoesNotExist:
                        pass
                
                # Créer ou mettre à jour la présence
                presence, created = PresenceProfesseur.objects.update_or_create(
                    professeur=professeur,
                    date=date_obj,
                    creneau=creneau,
                    defaults={
                        'present': present,
                        'commentaire': commentaire
                    }
                )
                
                if created:
                    messages.success(request, f"Présence enregistrée pour {professeur.nom}")
                else:
                    messages.success(request, f"Présence mise à jour pour {professeur.nom}")
                
            except (Professeur.DoesNotExist, ValueError):
                messages.error(request, "Une erreur s'est produite lors de l'enregistrement de la présence.")
        
        # Rediriger vers la même page avec les mêmes paramètres
        redirect_url = f"?date={date}"
        if creneau_id:
            redirect_url += f"&creneau={creneau_id}"
        return redirect(f"{request.path}{redirect_url}")
    
    # Récupérer les présences pour la date et le créneau sélectionnés
    presences = {}
    presence_records = PresenceProfesseur.objects.filter(date=selected_date)
    
    # Filtrer par créneau si un créneau est sélectionné
    if selected_creneau:
        presence_records = presence_records.filter(creneau=selected_creneau)
    
    for presence in presence_records:
        presences[presence.professeur.id] = presence
    
    # Construire une liste de tuples (professeur, presence) avec TOUS les professeurs
    professeurs_with_presence = []
    for prof in tous_les_professeurs:
        presence = presences.get(prof.id)
        professeurs_with_presence.append((prof, presence))
    
    # Statistiques de présence
    stats = {
        'total_professeurs': tous_les_professeurs.count(),
        'presents': 0,
        'absents_justifies': 0,
        'absents': 0
    }
    
    # Calculer les statistiques
    for _, presence in professeurs_with_presence:
        if presence:
            if presence.present:
                stats['presents'] += 1
            elif presence.justifie:
                stats['absents_justifies'] += 1
            else:
                stats['absents'] += 1
    
    return render(request, 'ecole_app/professeurs/gestion_presence.html', {
        'professeurs_with_presence': professeurs_with_presence,
        'selected_date': selected_date,
        'stats': stats,
        'creneaux': creneaux,
        'selected_creneau': selected_creneau
    })

@login_required
def rapport_presence_professeur(request):
    """Vue pour afficher un rapport des présences des professeurs"""
    professeurs = Professeur.objects.all().order_by('nom')
    
    # Filtrage par professeur
    professeur_id = request.GET.get('professeur')
    selected_professeur = None
    if professeur_id:
        try:
            selected_professeur = Professeur.objects.get(id=professeur_id)
        except Professeur.DoesNotExist:
            pass
    
    # Filtrage par période
    date_debut_str = request.GET.get('date_debut')
    date_fin_str = request.GET.get('date_fin')
    
    date_debut = None
    date_fin = None
    
    if date_debut_str:
        try:
            date_debut = datetime.datetime.strptime(date_debut_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    if date_fin_str:
        try:
            date_fin = datetime.datetime.strptime(date_fin_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    if not date_debut:
        # Par défaut, le début du mois courant
        today = timezone.now().date()
        date_debut = datetime.date(today.year, today.month, 1)
    
    if not date_fin:
        # Par défaut, aujourd'hui
        date_fin = timezone.now().date()
    
    # Récupérer les présences (du plus récent au plus ancien)
    presences_query = PresenceProfesseur.objects.filter(
        date__gte=date_debut,
        date__lte=date_fin
    ).order_by('-date', 'creneau__heure_debut', 'professeur__nom')
    
    if selected_professeur:
        presences_query = presences_query.filter(professeur=selected_professeur)
    
    presences = presences_query
    
    # Statistiques
    stats = {
        'total': presences.count(),
        'presents': presences.filter(present=True).count(),
        'absents': presences.filter(present=False, justifie=False).count(),
        'absents_justifies': presences.filter(present=False, justifie=True).count(),
    }
    
    if stats['total'] > 0:
        stats['taux_presence'] = round((stats['presents'] / stats['total']) * 100, 1)
    else:
        stats['taux_presence'] = 0
    
    context = {
        'professeurs': professeurs,
        'selected_professeur': selected_professeur,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'presences': presences,
        'stats': stats,
    }
    return render(request, 'ecole_app/professeurs/rapport_presence.html', context)

@login_required
def modifier_presence_professeur(request, presence_id):
    """Vue pour modifier une présence professeur"""
    presence = get_object_or_404(PresenceProfesseur, id=presence_id)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        commentaire = request.POST.get('commentaire', '')
        
        # Gestion des statuts
        present = False
        if status == 'present':
            present = True
        elif status == 'absent':
            present = False
        
        # Mise à jour de la présence
        presence.present = present
        presence.commentaire = commentaire
        presence.save()
        
        messages.success(request, f"Présence mise à jour pour {presence.professeur.nom}")
        return redirect('rapport_presence_professeur')
    
    return render(request, 'ecole_app/professeurs/modifier_presence.html', {
        'presence': presence
    })

@login_required
def supprimer_presence_professeur(request, presence_id):
    """Vue pour supprimer une présence professeur"""
    presence = get_object_or_404(PresenceProfesseur, id=presence_id)
    presence.delete()
    messages.success(request, "La présence a été supprimée avec succès.")
    
    # Rediriger vers la page du rapport
    return redirect('rapport_presence_professeur')
