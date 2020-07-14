from django.db import models

# Create your models here.


class OutlookServerDetails(models.Model):
    user_id = models.IntegerField(unique=True, null=False, blank=False)
    subscription_id = models.CharField(
        unique=True, max_length=200, blank=True, null=True)
    subscription_alive = models.BooleanField(default=False, blank=True)
    token_cache = models.TextField(max_length=10000, blank=True, null=True)
    token_alive = models.BooleanField(default=False, blank=True)
    new_message = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.subscription_id if self.subscription_id else ''

    class Meta:
        permissions = [
            ("mailserver_view", "Can view the mailserver details page"),
        ]
