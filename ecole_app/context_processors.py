from .models import SiteConfig

def site_name(request):
    return {
        'site_name': SiteConfig.get_site_name()
    }
