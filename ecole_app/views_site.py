from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SiteConfig
from .forms_site import SiteNameForm

@login_required
@user_passes_test(lambda u: u.is_superuser)
def modifier_nom_site(request):
    if request.method == 'POST':
        form = SiteNameForm(request.POST)
        if form.is_valid():
            SiteConfig.set_site_name(form.cleaned_data['site_name'])
            messages.success(request, "Le nom du site a été modifié avec succès.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form = SiteNameForm(initial={'site_name': SiteConfig.get_site_name()})
    return render(request, 'ecole_app/modifier_nom_site.html', {'form': form})
