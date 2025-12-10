from django.apps import AppConfig


class SolicitudesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.solicitudes"

    def ready(self):
        """
        Importa los signals cuando la app está lista
        """
        import apps.solicitudes.signals
