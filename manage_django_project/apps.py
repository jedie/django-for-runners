from django.apps import AppConfig


class ManageDjangoProjectConfig(AppConfig):
    name = "manage_django_project"
    verbose_name = "Manage Django Project"

    def ready(self):
        # Will init
        import manage_django_project.checks  # noqa
