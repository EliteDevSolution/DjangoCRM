from django.contrib import admin
from mailserver.models import OutlookServerDetails

# Register your models here.
@admin.register(OutlookServerDetails)
class OutlookServerDetailsAdmin(admin.ModelAdmin):
    list_display = ('user_id','subscription_id','new_message')