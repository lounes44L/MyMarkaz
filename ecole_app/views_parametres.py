from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import ParametreSite, Eleve
from django import forms

class ParametreSiteForm(forms.ModelForm):
    mettre_a_jour_eleves = forms.BooleanField(
        required=False, 
        initial=False,
        label="Mettre à jour tous les élèves existants",
        help_text="Cochez cette case pour appliquer ce montant à tous les élèves existants",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = ParametreSite
        fields = ['montant_defaut_eleve']
        widgets = {
            'montant_defaut_eleve': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }

@login_required
@user_passes_test(lambda u: u.is_superuser)
def parametres_site(request):
    """Vue pour modifier les paramètres du site"""
    # Récupérer ou créer l'instance unique des paramètres
    parametres, created = ParametreSite.objects.get_or_create(id=1)
    
    if request.method == 'POST':
        form = ParametreSiteForm(request.POST, instance=parametres)
        if form.is_valid():
            # Récupérer l'ancien montant avant de sauvegarder
            ancien_montant = parametres.montant_defaut_eleve
            
            # Sauvegarder les nouveaux paramètres
            form.save()
            nouveau_montant = form.cleaned_data['montant_defaut_eleve']
            
            # Vérifier si la case pour mettre à jour les élèves est cochée
            if form.cleaned_data.get('mettre_a_jour_eleves'):
                # Mettre à jour tous les élèves non archivés
                nb_eleves = Eleve.objects.filter(archive=False).update(montant_total=nouveau_montant)
                messages.success(
                    request, 
                    f"Les paramètres du site ont été mis à jour avec succès. "
                    f"Le montant de {nouveau_montant}€ a été appliqué à {nb_eleves} élève(s)."
                )
            else:
                messages.success(request, "Les paramètres du site ont été mis à jour avec succès.")
                
            return redirect('parametres_site')
    else:
        form = ParametreSiteForm(instance=parametres)
    
    return render(request, 'ecole_app/parametres/site.html', {
        'form': form,
        'title': 'Paramètres du site',
    })
