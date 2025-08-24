from django import forms
from .models import NoteExamen, Eleve, Classe
from datetime import date

class NoteExamenForm(forms.ModelForm):
    class Meta:
        model = NoteExamen
        fields = ['eleve', 'classe', 'titre', 'type_examen', 'sourate_concernee', 
                 'note', 'note_max', 'date_examen', 'commentaire']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Examen Sourate Al-Fatiha'
            }),
            'type_examen': forms.Select(attrs={'class': 'form-control'}),
            'sourate_concernee': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Sourate Al-Fatiha'
            }),
            'note': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.25',
                'min': '0'
            }),
            'note_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.25',
                'min': '0.25',
                'value': '20'
            }),
            'date_examen': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'value': date.today().strftime('%Y-%m-%d')
            }),
            'commentaire': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Commentaires optionnels sur la performance de l\'élève...'
            }),
            'eleve': forms.Select(attrs={'class': 'form-control'}),
            'classe': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'eleve': 'Élève',
            'classe': 'Classe',
            'titre': 'Titre de l\'examen',
            'type_examen': 'Type d\'examen',
            'sourate_concernee': 'Sourate concernée',
            'note': 'Note obtenue',
            'note_max': 'Note maximale',
            'date_examen': 'Date de l\'examen',
            'commentaire': 'Commentaires',
        }

    def __init__(self, *args, **kwargs):
        professeur = kwargs.pop('professeur', None)
        composante_id = kwargs.pop('composante_id', None)
        super().__init__(*args, **kwargs)
        
        if professeur and composante_id:
            # Filtrer les classes du professeur dans la composante sélectionnée
            self.fields['classe'].queryset = professeur.classes.filter(
                composante_id=composante_id
            ).order_by('nom')
            
            # Filtrer les élèves des classes du professeur
            self.fields['eleve'].queryset = Eleve.objects.filter(
                classes__professeur=professeur,
                composante_id=composante_id,
                archive=False
            ).distinct().order_by('nom', 'prenom')
        
        # Validation personnalisée
        self.fields['note'].help_text = "Note obtenue par l'élève"
        self.fields['note_max'].help_text = "Note maximale possible (généralement 20)"

    def clean(self):
        cleaned_data = super().clean()
        note = cleaned_data.get('note')
        note_max = cleaned_data.get('note_max')
        
        if note and note_max:
            if note > note_max:
                raise forms.ValidationError("La note obtenue ne peut pas être supérieure à la note maximale.")
            if note < 0:
                raise forms.ValidationError("La note ne peut pas être négative.")
            if note_max <= 0:
                raise forms.ValidationError("La note maximale doit être positive.")
        
        return cleaned_data

class FiltreNotesForm(forms.Form):
    """Formulaire pour filtrer les notes"""
    classe = forms.ModelChoiceField(
        queryset=Classe.objects.none(),
        required=False,
        empty_label="Toutes les classes",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    eleve = forms.ModelChoiceField(
        queryset=Eleve.objects.none(),
        required=False,
        empty_label="Tous les élèves",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    type_examen = forms.ChoiceField(
        choices=[('', 'Tous les types')] + NoteExamen.TYPE_EXAMEN_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Date de début"
    )
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label="Date de fin"
    )

    def __init__(self, *args, **kwargs):
        professeur = kwargs.pop('professeur', None)
        composante_id = kwargs.pop('composante_id', None)
        super().__init__(*args, **kwargs)
        
        if professeur and composante_id:
            self.fields['classe'].queryset = professeur.classes.filter(
                composante_id=composante_id
            ).order_by('nom')
            
            self.fields['eleve'].queryset = Eleve.objects.filter(
                classes__professeur=professeur,
                composante_id=composante_id,
                archive=False
            ).distinct().order_by('nom', 'prenom')
