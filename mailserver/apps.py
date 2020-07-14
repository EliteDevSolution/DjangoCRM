from django.apps import AppConfig


class MailServerConfig(AppConfig):
    name = 'mailserver'

    def ready(self):
        from .cron import start
        start()
