from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):
    name = 'for_runners'
    verbose_name = "ForRunners"

    def ready(self):
        import for_runners.checks  # noqa
