from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from .models import (Eleve, Professeur, Classe, Creneau, Paiement, AnneeScolaire, Charge, 
                     PresenceEleve, PresenceProfesseur, CarnetPedagogique, EcouteAvantMemo, 
                     Memorisation, Revision, Repetition, ListeAttente, NoteExamen)
from .sourate import Sourate, get_sourates_choices
from .form_mixins import ComposanteFormMixin

class CreneauForm(ComposanteFormMixin, forms.ModelForm):
    class Meta:
        model = Creneau
        fields = ['nom', 'jour', 'heure_debut', 'heure_fin']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du créneau', 'autofocus': True}),
            'jour': forms.Select(attrs={'class': 'form-control'}),
            'heure_debut': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'heure_fin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

class ProfesseurForm(ComposanteFormMixin, forms.ModelForm):
    nom_complet = forms.CharField(
        max_length=200, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom complet', 'autofocus': True, 'name': 'nom_complet'}),
        required=True,
        error_messages={'required': 'Le nom du professeur est obligatoire.'}
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    telephone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'})
    )
    indemnisation = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        initial=0.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        help_text="Indemnisation mensuelle"
    )
    
    class Meta:
        model = Professeur
        fields = ['nom', 'email', 'telephone', 'indemnisation']
        widgets = {
            'nom': forms.TextInput(attrs={'type': 'hidden'}),
        }
        field_classes = {'nom': forms.CharField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nom'].required = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nom'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        # Recopie le champ nom_complet dans nom
        nom_complet = cleaned_data.get('nom_complet', '').strip()
        if nom_complet:
            cleaned_data['nom'] = nom_complet
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Recopie nom_complet dans nom du modèle
        instance.nom = self.cleaned_data.get('nom_complet', '').strip()
        if commit:
            instance.save()
        return instance


class ChargeForm(forms.ModelForm):
    class Meta:
        model = Charge
        fields = ['categorie', 'montant', 'description', 'date', 'annee_scolaire']
        widgets = {
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'value': timezone.now().strftime('%Y-%m-%d')}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclure la catégorie 'indemnisation' qui est gérée séparément
        self.fields['categorie'].choices = [(k, v) for k, v in Charge.CATEGORIES if k != 'indemnisation']
        self.fields['annee_scolaire'].required = False
        self.fields['annee_scolaire'].empty_label = "Année scolaire active"


class IndemnisationForm(forms.ModelForm):
    class Meta:
        model = Charge
        fields = ['professeur', 'montant', 'description', 'date', 'annee_scolaire']
        widgets = {
            'professeur': forms.Select(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'value': timezone.now().strftime('%Y-%m-%d')}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['annee_scolaire'].required = False
        self.fields['annee_scolaire'].empty_label = "Année scolaire active"
        self.fields['professeur'].required = True


class PresenceProfesseurForm(forms.ModelForm):
    class Meta:
        model = PresenceProfesseur
        fields = ['professeur', 'date', 'present', 'justifie', 'commentaire']
        widgets = {
            'professeur': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'value': timezone.now().strftime('%Y-%m-%d')}),
            'present': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'justifie': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Copier le champ nom_complet dans nom du modèle
        instance.nom = self.data.get('nom_complet', '').strip()
        if commit:
            instance.save()
        return instance

class ClasseForm(ComposanteFormMixin, forms.ModelForm):
    class Meta:
        model = Classe
        fields = ['nom', 'professeur', 'creneau', 'capacite', 'annee_scolaire']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la classe', 'autofocus': True}),
            'professeur': forms.Select(attrs={'class': 'form-control'}),
            'creneau': forms.Select(attrs={'class': 'form-control'}),
            'capacite': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100, 'value': 20}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-control'}),
        }

class EleveForm(ComposanteFormMixin, forms.ModelForm):
    classes = forms.ModelMultipleChoiceField(
        queryset=Classe.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label='Classes'
    )
    
    class Meta:
        model = Eleve
        fields = ['nom', 'prenom', 'prenom_pere', 'prenom_mere', 'classes', 'date_naissance', 'telephone', 'telephone_secondaire', 'email', 'adresse', 'annee_scolaire', 'montant_total', 'remarque']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l\'élève'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom de l\'élève'}),
            'prenom_pere': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom du père'}),
            'prenom_mere': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom de la mère'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
            'telephone_secondaire': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone secondaire'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Adresse', 'rows': 3}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-control'}),
            'montant_total': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'remarque': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Remarque (facultatif)', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        # Définir le montant par défaut avant d'initialiser le formulaire
        if 'initial' not in kwargs:
            kwargs['initial'] = {}
        if 'montant_total' not in kwargs.get('initial', {}):
            # Utiliser le montant par défaut des paramètres du site
            from .models import ParametreSite
            kwargs['initial']['montant_total'] = ParametreSite.get_montant_defaut()
            
        super().__init__(*args, **kwargs)
        # Rendre le champ montant_total optionnel
        self.fields['montant_total'].required = False
        composante_id = None
        if 'request' in kwargs:
            request = kwargs['request']
            composante_id = request.session.get('composante_id')
        if not composante_id:
            composante_id = self.initial.get('composante_id') or self.data.get('composante')
        if composante_id:
            # Filtrer les classes par composante
            qs_classes = Classe.objects.filter(composante_id=composante_id).order_by('nom')
            if qs_classes.exists():
                self.fields['classes'].queryset = qs_classes
            else:
                self.fields['classes'].queryset = Classe.objects.all().order_by('nom')
                self.fields['classes'].help_text = "Aucune classe pour la composante active. Toutes les classes sont proposées."
        else:
            self.fields['classes'].queryset = Classe.objects.all().order_by('nom')
            self.fields['classes'].help_text = "Sélectionnez une ou plusieurs classes."

class ListeAttenteForm(forms.ModelForm):
    class Meta:
        model = ListeAttente
        fields = ['nom', 'prenom', 'date_naissance', 'telephone', 'email', 'remarque']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l’élève', 'autofocus': True}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'jj/mm/aaaa'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'remarque': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Remarque (facultatif)', 'rows': 2}),
        }


class DesarchivageEleveForm(forms.ModelForm):
    class Meta:
        model = Eleve
        fields = ['classe', 'creneaux']
        widgets = {
            
            'creneaux': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '5'}),
        }

class EleveRapideForm(ComposanteFormMixin, forms.ModelForm):
    classes = forms.ModelMultipleChoiceField(
        queryset=Classe.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label='Classes'
    )
    
    class Meta:
        model = Eleve
        fields = ['nom', 'prenom', 'prenom_pere', 'prenom_mere', 'classes', 'telephone', 'telephone_secondaire']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l\'élève'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom de l\'élève'}),
            'prenom_pere': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom du père'}),
            'prenom_mere': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom de la mère'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
            'telephone_secondaire': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone secondaire'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        composante_id = None
        if 'request' in kwargs:
            request = kwargs['request']
            composante_id = request.session.get('composante_id')
        if not composante_id:
            composante_id = self.initial.get('composante_id') or self.data.get('composante')
        if composante_id:
            # Filtrer les classes par composante
            qs_classes = Classe.objects.filter(composante_id=composante_id).order_by('nom')
            if qs_classes.exists():
                self.fields['classes'].queryset = qs_classes
            else:
                self.fields['classes'].queryset = Classe.objects.all().order_by('nom')
        else:
            self.fields['classes'].queryset = Classe.objects.all().order_by('nom')

class PaiementForm(ComposanteFormMixin, forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['eleve', 'montant', 'date', 'methode', 'commentaire', 'annee_scolaire']
        widgets = {
            'eleve': forms.Select(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'methode': forms.Select(attrs={'class': 'form-control'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Commentaire', 'rows': 2}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.initial_montant = None
        instance = kwargs.get('instance', None)
        if instance:
            self.initial_montant = instance.montant
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        paiement = super().save(commit=False)
        if not paiement.annee_scolaire:
            from .models import AnneeScolaire
            annee_active = AnneeScolaire.objects.filter(active=True).first()
            paiement.annee_scolaire = annee_active
        
        # Check if this is a modification and the amount has changed
        is_modification = paiement.pk is not None
        montant_changed = is_modification and self.initial_montant is not None and self.initial_montant != paiement.montant
        
        if commit:
            paiement.save()
            self.save_m2m()
            
            # Create a history entry if this is a modification and the amount has changed
            if montant_changed:
                from .models import PaiementHistorique
                PaiementHistorique.objects.create(
                    paiement=paiement,
                    montant=paiement.montant,
                    date=paiement.date,
                    methode=paiement.methode,
                    commentaire=f"Modification du montant de {self.initial_montant} à {paiement.montant}"
                )
        
        return paiement

class ImportDataForm(forms.Form):
    """Formulaire pour importer des élèves depuis un fichier CSV ou Excel"""
    TYPE_CHOIX = (
        ('csv', 'CSV'),
        ('excel', 'Excel (XLSX)'),
    )
    
    fichier_import = forms.FileField(
        label="Fichier à importer",
        help_text="Colonnes requises: nom, prenom. Colonnes optionnelles: classe_id, creneau_id, date_naissance, telephone, email, adresse"
    )
    type_fichier = forms.ChoiceField(
        choices=TYPE_CHOIX,
        label="Type de fichier",
        initial='excel',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
class ExportDataForm(forms.Form):
    """Formulaire pour exporter les données"""
    CHOIX_EXPORT = (
        ('eleves', 'Élèves'),
        ('professeurs', 'Professeurs'),
        ('classes', 'Classes'),
        ('creneaux', 'Créneaux'),
        ('paiements', 'Paiements'),
        ('charges', 'Charges'),
        ('presences_eleves', 'Présences élèves'),
        ('presences_professeurs', 'Présences professeurs'),
        ('tout', 'Toutes les données'),
    )
    
    FORMAT_CHOIX = (
        ('excel', 'Excel (XLSX)'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    )
    
    type_export = forms.ChoiceField(
        choices=CHOIX_EXPORT,
        label="Données à exporter",
        initial='eleves',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    format_export = forms.ChoiceField(
        choices=FORMAT_CHOIX,
        label="Format d'export",
        initial='excel',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    annee_scolaire = forms.ModelChoiceField(
        queryset=AnneeScolaire.objects.all(),
        required=False,
        empty_label="Toutes les années scolaires",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class AnneeScolaireForm(forms.ModelForm):
    class Meta:
        model = AnneeScolaire
        fields = ['nom', 'date_debut', 'date_fin', 'active']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2023-2024', 'autofocus': True}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ChargeForm(forms.ModelForm):
    class Meta:
        model = Charge
        fields = ['categorie', 'montant', 'description', 'date', 'professeur', 'annee_scolaire']
        widgets = {
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description', 'rows': 2}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'professeur': forms.Select(attrs={'class': 'form-control'}),
            'annee_scolaire': forms.Select(attrs={'class': 'form-control'}),
        }

class PresenceEleveForm(forms.ModelForm):
    class Meta:
        model = PresenceEleve
        fields = ['eleve', 'date', 'present', 'justifie', 'commentaire', 'classe', 'creneau']
        widgets = {
            'eleve': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'present': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'justifie': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Commentaire', 'rows': 2}),
            
            'creneau': forms.Select(attrs={'class': 'form-control'}),
        }

class PresenceProfesseurForm(forms.ModelForm):
    class Meta:
        model = PresenceProfesseur
        fields = ['professeur', 'date', 'creneau', 'present', 'justifie', 'commentaire']
        widgets = {
            'professeur': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'creneau': forms.Select(attrs={'class': 'form-control'}),
            'present': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'justifie': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Commentaire', 'rows': 2}),
        }

class PresenceMultipleForm(forms.Form):
    """Formulaire pour gérer les présences de plusieurs élèves à la fois"""
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date"
    )
    classe = forms.ModelChoiceField(
        queryset=Classe.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Classe"
    )
    creneau = forms.ModelChoiceField(
        queryset=Creneau.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Créneau"
    )

class UserPreferencesForm(forms.Form):
    """Formulaire pour les préférences utilisateur"""
    annee_scolaire_active = forms.ModelChoiceField(
        queryset=AnneeScolaire.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Année scolaire active"
    )
    theme = forms.ChoiceField(
        choices=(
            ('light', 'Thème clair'),
            ('dark', 'Thème sombre'),
            ('auto', 'Automatique (selon préférences du navigateur)')
        ),
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='auto',
        label="Thème"
    )


# Formulaires pour le carnet pédagogique

class CarnetPedagogiqueForm(forms.ModelForm):
    """Formulaire pour créer ou éditer un carnet pédagogique"""
    class Meta:
        model = CarnetPedagogique
        fields = ['eleve']
        widgets = {
            'eleve': forms.Select(attrs={'class': 'form-control'}),
        }

class EcouteAvantMemoForm(forms.ModelForm):
    """Formulaire pour les sessions d'écoute avant mémorisation"""
    sourate = forms.ChoiceField(
        choices=get_sourates_choices,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'sourate-select-ecoute'})
    )
    
    class Meta:
        model = EcouteAvantMemo
        fields = ['date', 'debut_page', 'fin_page', 'enseignant', 'remarques']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'value': timezone.now().strftime('%Y-%m-%d')}),
            'debut_page': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '604', 'placeholder': 'Page de début'}),
            'fin_page': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '604', 'placeholder': 'Page de fin'}),
            'enseignant': forms.Select(attrs={'class': 'form-control'}),
            'remarques': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Remarques (facultatif)', 'rows': 2}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Le champ sourate n'est pas dans le modèle, donc on le retire des données à sauvegarder
        self.fields['sourate'].required = False

class MemorisationForm(forms.ModelForm):
    """Formulaire pour les sessions de mémorisation"""
    sourate = forms.ChoiceField(
        choices=get_sourates_choices,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'sourate-select'})
    )
    
    class Meta:
        model = Memorisation
        fields = ['date', 'sourate', 'debut_page', 'fin_page', 'enseignant', 'remarques']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'value': timezone.now().strftime('%Y-%m-%d')}),
            'debut_page': forms.Select(attrs={'class': 'form-control', 'id': 'debut-page-select', 'disabled': 'disabled'}),
            'fin_page': forms.Select(attrs={'class': 'form-control', 'id': 'fin-page-select', 'disabled': 'disabled'}),
            'enseignant': forms.Select(attrs={'class': 'form-control'}),
            'remarques': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Remarques (facultatif)', 'rows': 2}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Le champ sourate n'est pas dans le modèle, donc on le retire des données à sauvegarder
        self.fields['sourate'].required = False

class RevisionForm(forms.ModelForm):
    """Formulaire pour les révisions hebdomadaires"""
    class Meta:
        model = Revision
        fields = ['semaine', 'date', 'jour', 'nombre_hizb']
        widgets = {
            'semaine': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '52', 'placeholder': 'Numéro de semaine'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'value': timezone.now().strftime('%Y-%m-%d')}),
            'jour': forms.Select(attrs={'class': 'form-control'}),
            'nombre_hizb': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'placeholder': 'Nombre de Hizb révisés'}),
        }

class RepetitionForm(forms.ModelForm):
    """Formulaire pour les répétitions par page et sourate"""
    sourate_select = forms.ChoiceField(
        choices=get_sourates_choices,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'sourate-select-repetition'}),
        required=True,
        label="Sourate"
    )
    
    class Meta:
        model = Repetition
        fields = ['sourate_select', 'sourate', 'page', 'nombre_repetitions']
        widgets = {
            'sourate': forms.HiddenInput(),  # On cache le champ texte original
            # On utilise readonly au lieu de disabled pour que la valeur soit envoyée
            'page': forms.Select(attrs={'class': 'form-control', 'id': 'page-select-repetition'}),
            'nombre_repetitions': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'value': '1', 'placeholder': 'Nombre de répétitions'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre les champs obligatoires
        self.fields['page'].required = True
        self.fields['nombre_repetitions'].required = True
        
        # Le champ sourate est géré par sourate_select, donc on le rend non obligatoire
        self.fields['sourate'].required = False
        
        # Ajouter des messages d'erreur explicites
        self.fields['page'].error_messages = {'required': 'Veuillez sélectionner une page'}
        self.fields['nombre_repetitions'].error_messages = {'required': 'Veuillez indiquer le nombre de répétitions'}
        
        # Si nous sommes en mode POST, pré-remplir le champ sourate à partir de sourate_select
        if 'data' in kwargs and kwargs['data'] and 'sourate_select' in kwargs['data']:
            try:
                from .sourate import SOURATES
                sourate_index = int(kwargs['data']['sourate_select'])
                sourate = SOURATES[sourate_index]
                self.initial['sourate'] = sourate.nom
            except (ValueError, IndexError, KeyError):
                pass
        
    def clean(self):
        cleaned_data = super().clean()
        # On récupère le nom de la sourate à partir de l'index sélectionné
        sourate_index = cleaned_data.get('sourate_select')
        if sourate_index:
            from .sourate import SOURATES
            try:
                sourate = SOURATES[int(sourate_index)]
                cleaned_data['sourate'] = sourate.nom
                # Assigner directement la valeur au champ sourate
                self.data = self.data.copy()  # Rendre mutable
                self.data['sourate'] = sourate.nom
            except (IndexError, ValueError):
                self.add_error('sourate_select', 'Sourate invalide')
        else:
            self.add_error('sourate_select', 'Veuillez sélectionner une sourate')
            
        # Vérifier que le nombre de répétitions est positif
        nombre_repetitions = cleaned_data.get('nombre_repetitions')
        if nombre_repetitions is not None and nombre_repetitions < 1:
            self.add_error('nombre_repetitions', 'Le nombre de répétitions doit être supérieur à 0')
            
        return cleaned_data
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # S'assurer que le champ sourate est correctement rempli
        if not instance.sourate and 'sourate_select' in self.cleaned_data:
            sourate_index = self.cleaned_data['sourate_select']
            try:
                from .sourate import SOURATES
                sourate = SOURATES[int(sourate_index)]
                instance.sourate = sourate.nom
            except (IndexError, ValueError):
                pass
                
        if commit:
            instance.save()
            
        return instance


class NoteExamenForm(forms.ModelForm):
    """Formulaire pour les notes d'examen"""
    class Meta:
        model = NoteExamen
        fields = ['eleve', 'classe', 'titre', 'type_examen', 'sourate_concernee', 'note', 'note_max', 'date_examen', 'commentaire']
        widgets = {
            'eleve': forms.Select(attrs={'class': 'form-control'}),
            'classe': forms.Select(attrs={'class': 'form-control'}),
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Titre de l'examen"}),
            'type_examen': forms.Select(attrs={'class': 'form-control'}),
            'sourate_concernee': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sourate concernée (optionnel)'}),
            'note': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '20'}),
            'note_max': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '1', 'value': '20'}),
            'date_examen': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'value': timezone.now().strftime('%Y-%m-%d')}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Commentaires', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.professeur = kwargs.pop('professeur', None)
        self.composante_id = kwargs.pop('composante_id', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les élèves et les classes selon le professeur et la composante
        if self.professeur and self.composante_id:
            # Récupérer les classes du professeur dans la composante actuelle
            classes = self.professeur.classes.filter(composante_id=self.composante_id)
            self.fields['classe'].queryset = classes
            
            # Récupérer TOUS les élèves des classes du professeur sans filtrer par composante
            eleves = Eleve.objects.filter(
                classes__in=self.professeur.classes.all(),
                archive=False
            ).distinct().order_by('nom', 'prenom')
            self.fields['eleve'].queryset = eleves
        
        # Si c'est une modification, désactiver le changement d'élève et de classe
        if self.instance and self.instance.pk:
            self.fields['eleve'].disabled = True
            self.fields['classe'].disabled = True
