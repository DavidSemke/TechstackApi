from django.apps import AppConfig


class PostsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.posts"

    def ready(self):
        # Implicitly connect signal handlers
        from . import signals as signals

        return super().ready()
