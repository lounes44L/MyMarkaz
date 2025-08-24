from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.db.models.functions import TruncMonth
from .models import Charge, Professeur, AnneeScolaire, Paiement
from .forms import ChargeForm, IndemnisationForm, PaiementForm
import datetime
import locale
from collections import defaultdict

@login_required
def liste_charges(request):
    """Vue pour afficher la liste des charges"""
    charges = Charge.objects.exclude(categorie='indemnisation').order_by('-date')
    
    # Statistiques
    total_charges = charges.aggregate(total=Sum('montant')).get('total') or 0
    
    # Grouper les charges par mois
    charges_par_mois = Charge.objects.exclude(categorie='indemnisation')\
        .annotate(mois=TruncMonth('date'))\
        .values('mois')\
        .annotate(total=Sum('montant'))\
        .order_by('-mois')
    
    # Filtrage par année scolaire si spécifiée
    annee_id = request.GET.get('annee')
    annees = AnneeScolaire.objects.all().order_by('-date_debut')
    annee_active = None
    
    if annee_id:
        try:
            annee_active = AnneeScolaire.objects.get(id=annee_id)
            charges = charges.filter(annee_scolaire=annee_active)
            charges_par_mois = charges_par_mois.filter(annee_scolaire=annee_active)
        except AnneeScolaire.DoesNotExist:
            pass
    else:
        # Par défaut, utiliser l'année active
        try:
            annee_active = AnneeScolaire.objects.get(active=True)
            charges = charges.filter(annee_scolaire=annee_active)
            charges_par_mois = charges_par_mois.filter(annee_scolaire=annee_active)
        except AnneeScolaire.DoesNotExist:
            pass
    
    # Traitement du formulaire d'ajout de charge
    if request.method == 'POST':
        form = ChargeForm(request.POST)
        if form.is_valid():
            charge = form.save(commit=False)
            if not charge.annee_scolaire and annee_active:
                charge.annee_scolaire = annee_active
                
            # Vérifier si une charge identique existe déjà
            charge_existante = Charge.objects.filter(
                description=charge.description,
                categorie=charge.categorie,
                montant=charge.montant,
                date=charge.date,
                annee_scolaire=charge.annee_scolaire
            ).first()
            
            if charge_existante:
                messages.warning(request, "Une charge identique existe déjà dans le système. Aucune nouvelle charge n'a été ajoutée.")
            else:
                charge.save()
                messages.success(request, "La charge a été ajoutée avec succès.")
                
            return redirect('liste_charges')
    else:
        form = ChargeForm()
    
    # Configuration de la localisation pour les mois en français
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'fr_FR')
        except locale.Error:
            # Fallback si les locales français ne sont pas disponibles
            pass
    
    context = {
        'charges': charges,
        'form': form,
        'total_charges': total_charges,
        'charges_par_mois': charges_par_mois,
        'annees': annees,
        'annee_active': annee_active,
    }
    return render(request, 'ecole_app/comptabilite/charges.html', context)

@login_required
def supprimer_charge(request, charge_id):
    """Vue pour supprimer une charge"""
    charge = get_object_or_404(Charge, id=charge_id)
    
    if request.method == 'POST':
        charge.delete()
        messages.success(request, "La charge a été supprimée avec succès.")
        return redirect('liste_charges')
    
    context = {
        'charge': charge,
    }
    return render(request, 'ecole_app/comptabilite/confirmer_suppression_charge.html', context)

@login_required
def liste_indemnisations(request):
    """Vue pour afficher la liste des indemnisations des professeurs"""
    indemnisations = Charge.objects.filter(categorie='indemnisation').order_by('-date')
    professeurs = Professeur.objects.all().order_by('nom')
    professeur_selectionne = None
    
    # Statistiques
    total_indemnisations = indemnisations.aggregate(total=Sum('montant')).get('total') or 0
    
    # Filtrage par professeur si spécifié
    professeur_id = request.GET.get('professeur')
    if professeur_id:
        try:
            professeur_selectionne = Professeur.objects.get(id=professeur_id)
            indemnisations = indemnisations.filter(professeur=professeur_selectionne)
        except Professeur.DoesNotExist:
            pass
    
    # Grouper les indemnisations par mois
    indemnisations_par_mois_query = Charge.objects.filter(categorie='indemnisation')
    
    # Appliquer le filtre par professeur aux données mensuelles si nécessaire
    if professeur_selectionne:
        indemnisations_par_mois_query = indemnisations_par_mois_query.filter(professeur=professeur_selectionne)
        
    indemnisations_par_mois = indemnisations_par_mois_query\
        .annotate(mois=TruncMonth('date'))\
        .values('mois')\
        .annotate(total=Sum('montant'))\
        .order_by('-mois')
    
    # Filtrage par année scolaire si spécifiée
    annee_id = request.GET.get('annee')
    annees = AnneeScolaire.objects.all().order_by('-date_debut')
    annee_active = None
    
    if annee_id:
        try:
            annee_active = AnneeScolaire.objects.get(id=annee_id)
            indemnisations = indemnisations.filter(annee_scolaire=annee_active)
            indemnisations_par_mois = indemnisations_par_mois.filter(annee_scolaire=annee_active)
        except AnneeScolaire.DoesNotExist:
            pass
    else:
        # Par défaut, utiliser l'année active
        try:
            annee_active = AnneeScolaire.objects.get(active=True)
            indemnisations = indemnisations.filter(annee_scolaire=annee_active)
            indemnisations_par_mois = indemnisations_par_mois.filter(annee_scolaire=annee_active)
        except AnneeScolaire.DoesNotExist:
            pass
    
    # Formulaire d'ajout d'indemnisation
    form = ChargeForm(initial={'categorie': 'indemnisation'})
    
    if request.method == 'POST':
        form = ChargeForm(request.POST)
        if form.is_valid():
            indemnisation = form.save(commit=False)
            indemnisation.categorie = 'indemnisation'
            if not indemnisation.annee_scolaire and annee_active:
                indemnisation.annee_scolaire = annee_active
                
            # Vérifier si une indemnisation identique existe déjà
            indemnisation_existante = Charge.objects.filter(
                description=indemnisation.description,
                categorie='indemnisation',
                montant=indemnisation.montant,
                date=indemnisation.date,
                professeur=indemnisation.professeur,
                annee_scolaire=indemnisation.annee_scolaire
            ).first()
            
            if indemnisation_existante:
                messages.warning(request, "Une indemnisation identique existe déjà dans le système. Aucune nouvelle indemnisation n'a été ajoutée.")
            else:
                indemnisation.save()
                messages.success(request, "L'indemnisation a été ajoutée avec succès.")
                
            return redirect('liste_indemnisations')
    else:
        form = IndemnisationForm()
    
    # Configuration de la localisation pour les mois en français
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'fr_FR')
        except locale.Error:
            # Fallback si les locales français ne sont pas disponibles
            pass
    
    context = {
        'indemnisations': indemnisations,
        'professeurs': professeurs,
        'professeur_selectionne': professeur_selectionne,
        'form': form,
        'total_indemnisations': total_indemnisations,
        'indemnisations_par_mois': indemnisations_par_mois,
        'annees': annees,
        'annee_active': annee_active,
    }
    return render(request, 'ecole_app/comptabilite/indemnisations.html', context)

@login_required
def supprimer_indemnisation(request, indemnisation_id):
    """Vue pour supprimer une indemnisation"""
    indemnisation = get_object_or_404(Charge, id=indemnisation_id, categorie='indemnisation')
    
    if request.method == 'POST':
        indemnisation.delete()
        messages.success(request, "L'indemnisation a été supprimée avec succès.")
        return redirect('liste_indemnisations')
    
    context = {
        'indemnisation': indemnisation,
    }
    return render(request, 'ecole_app/comptabilite/confirmer_suppression_indemnisation.html', context)

@login_required
def statistiques_paiements(request):
    """Vue pour afficher les statistiques des paiements"""
    paiements = Paiement.objects.all()
    
    # Statistiques générales
    total_paiements = paiements.aggregate(total=Sum('montant')).get('total') or 0
    nombre_paiements = paiements.count()
    
    # Calcul de la moyenne des paiements
    moyenne_paiement = total_paiements / nombre_paiements if nombre_paiements > 0 else 0
    
    # Grouper par mois
    paiements_par_mois = paiements\
        .annotate(mois=TruncMonth('date'))\
        .values('mois')\
        .annotate(total=Sum('montant'), count=Count('id'))\
        .order_by('-mois')
    
    # Grouper par méthode de paiement
    paiements_par_methode = paiements\
        .values('methode')\
        .annotate(total=Sum('montant'), count=Count('id'))\
        .order_by('-total')
    
    # Paiements par élève (top 10)
    top_eleves = paiements\
        .values('eleve__nom', 'eleve__prenom')\
        .annotate(total=Sum('montant'), count=Count('id'))\
        .order_by('-total')[:10]
    
    context = {
        'total_paiements': total_paiements,
        'nombre_paiements': nombre_paiements,
        'moyenne_paiement': moyenne_paiement,
        'paiements_par_mois': paiements_par_mois,
        'paiements_par_methode': paiements_par_methode,
        'top_eleves': top_eleves,
    }
    return render(request, 'ecole_app/comptabilite/statistiques_paiements.html', context)

@login_required
def saisie_paiement(request):
    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Paiement ajouté avec succès.")
            return redirect('dashboard')  # Redirect to dashboard; adjust if needed
    else:
        form = PaiementForm()
    return render(request, 'ecole_app/comptabilite/saisie_paiement.html', {'form': form})
