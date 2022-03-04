from django.apps import AppConfig


class AdminAreaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_area'
    verbose_name = "Administrator's Area"

    def ready(self):
        import admin_area.signals 