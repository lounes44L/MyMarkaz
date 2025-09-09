from django.apps import AppConfig


class EcoleAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ecole_app'
    
    def ready(self):
        import ecole_app.signals
