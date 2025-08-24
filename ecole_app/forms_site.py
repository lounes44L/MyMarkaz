from django import forms

class SiteNameForm(forms.Form):
    site_name = forms.CharField(
        label="Nom du site",
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom du site…'
        })
    )
