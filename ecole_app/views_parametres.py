from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import ParametreSite
from django import forms

class ParametreSiteForm(forms.ModelForm):
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
            form.save()
            messages.success(request, "Les paramètres du site ont été mis à jour avec succès.")
            return redirect('parametres_site')
    else:
        form = ParametreSiteForm(instance=parametres)
    
    return render(request, 'ecole_app/parametres/site.html', {
        'form': form,
        'title': 'Paramètres du site',
    })
