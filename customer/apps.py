from django.apps import AppConfig


class CustomerConfig(AppConfig):
    name = 'customer'

    def ready(self):
        """When application is ready, load the following"""
        from .signals import user_signed_up_
