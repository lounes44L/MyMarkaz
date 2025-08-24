from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import TruncMonth, ExtractMonth, ExtractYear
from .models import Charge, AnneeScolaire, Paiement
import datetime
import json
import calendar
from decimal import Decimal

# Custom JSON encoder to handle Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

@login_required
def bilan_financier(request):
    """Vue pour afficher le bilan financier avec des graphiques et statistiques"""
    
    # Récupérer les paramètres de filtrage
    annee_id = request.GET.get('annee')
    periode = request.GET.get('periode', 'annee')
    mois = int(request.GET.get('mois', datetime.datetime.now().month))
    
    # Récupérer toutes les années scolaires
    annees = AnneeScolaire.objects.all().order_by('-date_debut')
    annee_active = None
    
    # Filtrer par année scolaire si spécifiée
    if annee_id:
        try:
            annee_active = AnneeScolaire.objects.get(id=annee_id)
        except AnneeScolaire.DoesNotExist:
            pass
    else:
        # Par défaut, utiliser l'année active
        try:
            annee_active = AnneeScolaire.objects.get(active=True)
        except AnneeScolaire.DoesNotExist:
            if annees.exists():
                annee_active = annees.first()
    
    # Initialiser les queryset de base
    charges_qs = Charge.objects.exclude(categorie='indemnisation')
    indemnisations_qs = Charge.objects.filter(categorie='indemnisation')
    paiements_qs = Paiement.objects.all()
    
    # Appliquer le filtre d'année scolaire
    if annee_active:
        charges_qs = charges_qs.filter(annee_scolaire=annee_active)
        indemnisations_qs = indemnisations_qs.filter(annee_scolaire=annee_active)
        paiements_qs = paiements_qs.filter(annee_scolaire=annee_active)
    
    # Appliquer les filtres de période
    date_debut = None
    date_fin = None
    
    if periode == 'mois':
        # Filtrer par mois
        annee_courante = datetime.datetime.now().year
        if annee_active:
            # Utiliser l'année de l'année scolaire active
            if mois >= 9:  # Si mois >= septembre, on est dans la première partie de l'année scolaire
                annee_courante = annee_active.date_debut.year
            else:  # Sinon on est dans la deuxième partie
                annee_courante = annee_active.date_fin.year
        
        date_debut = datetime.date(annee_courante, mois, 1)
        # Dernier jour du mois
        dernier_jour = calendar.monthrange(annee_courante, mois)[1]
        date_fin = datetime.date(annee_courante, mois, dernier_jour)
        

    # Appliquer les filtres de date si nécessaire
    if date_debut and date_fin:
        charges_qs = charges_qs.filter(date__gte=date_debut, date__lte=date_fin)
        indemnisations_qs = indemnisations_qs.filter(date__gte=date_debut, date__lte=date_fin)
        paiements_qs = paiements_qs.filter(date__gte=date_debut, date__lte=date_fin)
    
    # Calculer les totaux
    total_charges = charges_qs.aggregate(total=Sum('montant')).get('total') or 0
    total_indemnisations = indemnisations_qs.aggregate(total=Sum('montant')).get('total') or 0
    total_entrees = paiements_qs.aggregate(total=Sum('montant')).get('total') or 0
    solde = total_entrees - (total_charges + total_indemnisations)
    
    # Répartition des charges par catégorie
    charges_par_categorie = []
    categories_charges = charges_qs.values('categorie').annotate(
        total=Sum('montant')
    ).order_by('-total')
    
    for cat in categories_charges:
        categorie_display = dict(Charge.CATEGORIES).get(cat['categorie'], cat['categorie'])
        pourcentage = round((cat['total'] / total_charges * 100) if total_charges > 0 else 0, 2)
        charges_par_categorie.append({
            'categorie': cat['categorie'],
            'categorie_display': categorie_display,
            'total': cat['total'],
            'pourcentage': pourcentage
        })
    
    # Répartition des entrées par type (paiements)
    entrees_par_type = []
    types_paiement = paiements_qs.values('methode').annotate(
        total=Sum('montant')
    ).order_by('-total')
    
    for type_p in types_paiement:
        type_display = dict(Paiement.METHODES).get(type_p['methode'], type_p['methode']) if hasattr(Paiement, 'METHODES') else type_p['methode']
        pourcentage = round((type_p['total'] / total_entrees) * 100, 2) if total_entrees > 0 else 0
        entrees_par_type.append({
            'type': type_p['methode'],
            'type_display': type_display,
            'total': type_p['total'],
            'pourcentage': pourcentage
        })
    
    # Données pour le graphique d'évolution mensuelle
    mois_labels = []
    donnees_entrees = []
    donnees_charges = []
    donnees_indemnisations = []
    donnees_solde = []
    
    # Déterminer la période pour l'évolution mensuelle
    if annee_active:
        date_debut_graph = annee_active.date_debut
        date_fin_graph = annee_active.date_fin
    else:
        # Par défaut, utiliser l'année civile en cours
        annee_courante = datetime.datetime.now().year
        date_debut_graph = datetime.date(annee_courante, 1, 1)
        date_fin_graph = datetime.date(annee_courante, 12, 31)
    
    # Générer les données mensuelles
    current_date = date_debut_graph
    while current_date <= date_fin_graph:
        month_name = current_date.strftime("%b %Y")
        mois_labels.append(month_name)
        
        month_start = datetime.date(current_date.year, current_date.month, 1)
        month_end = datetime.date(
            current_date.year, 
            current_date.month, 
            calendar.monthrange(current_date.year, current_date.month)[1]
        )
        
        # Calculer les totaux pour ce mois
        entrees_mois = paiements_qs.filter(
            date__gte=month_start, 
            date__lte=month_end
        ).aggregate(total=Sum('montant')).get('total') or 0
        
        charges_mois = charges_qs.filter(
            date__gte=month_start, 
            date__lte=month_end
        ).aggregate(total=Sum('montant')).get('total') or 0
        
        indemnisations_mois = indemnisations_qs.filter(
            date__gte=month_start, 
            date__lte=month_end
        ).aggregate(total=Sum('montant')).get('total') or 0
        
        solde_mois = entrees_mois - (charges_mois + indemnisations_mois)
        
        donnees_entrees.append(entrees_mois)
        donnees_charges.append(charges_mois)
        donnees_indemnisations.append(indemnisations_mois)
        donnees_solde.append(solde_mois)
        
        # Passer au mois suivant
        if current_date.month == 12:
            current_date = datetime.date(current_date.year + 1, 1, 1)
        else:
            current_date = datetime.date(current_date.year, current_date.month + 1, 1)
    
    context = {
        'annees': annees,
        'annee_active': annee_active,
        'periode': periode,
        'mois': mois,

        'total_charges': total_charges,
        'total_indemnisations': total_indemnisations,
        'total_entrees': total_entrees,
        'solde': solde,
        'charges_par_categorie': [
            {**c, 'total': float(c['total']) if isinstance(c['total'], (int, float, complex)) or c['total'] is None else float(c['total'])} for c in charges_par_categorie
        ],
        'entrees_par_type': [
            {**e, 'total': float(e['total']) if isinstance(e['total'], (int, float, complex)) or e['total'] is None else float(e['total'])} for e in entrees_par_type
        ],
        'charges_labels': json.dumps([c['categorie_display'] for c in charges_par_categorie], ensure_ascii=False, cls=DecimalEncoder),
        'charges_data': json.dumps([c['total'] for c in charges_par_categorie], cls=DecimalEncoder),
        'labels_mois': json.dumps(mois_labels, cls=DecimalEncoder),
        'donnees_entrees': json.dumps(donnees_entrees, cls=DecimalEncoder),
        'donnees_charges': json.dumps(donnees_charges, cls=DecimalEncoder),
        'donnees_indemnisations': json.dumps(donnees_indemnisations, cls=DecimalEncoder),
        'donnees_solde': json.dumps(donnees_solde, cls=DecimalEncoder),
    }
    
    return render(request, 'ecole_app/comptabilite/bilan_financier.html', context)
