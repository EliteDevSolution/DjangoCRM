from allauth.account.signals import user_signed_up
from django.contrib.auth.models import Permission, User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile

permissions = [
    "customer_list",
    "customer_view",
    "deposit_list",
    "deposit_view",
    "on_file_list",
    "on_file_view",
    "order_list",
    "order_view",
    "installation_list",
    "installation_view",
    "account_list",
    "account_view",
    "service_list",
    "service_view",
    "finished_list",
    "finished_view",
    "reports_view",
]


@receiver(user_signed_up)
def user_signed_up_(request, user, **kwargs):
    """Signal to assign all permissions to a user when signing up"""
    for permission in permissions:
        user.user_permissions.add(Permission.objects.get(codename=permission))


@receiver(post_save, sender=User)
def user_post_save(sender, instance, **kwargs):
    """Assign a profile when a user is created"""
    if not Profile.objects.filter(user_id=instance.id).exists():
        profile = Profile(user=instance)
        profile.save()
