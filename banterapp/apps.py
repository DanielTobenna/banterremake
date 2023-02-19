from django.apps import AppConfig


class BanterappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'banterapp'

    def ready(self):
    	import banterapp.signals
