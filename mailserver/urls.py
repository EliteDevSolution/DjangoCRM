from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.conf.urls import url, include


urlpatterns = [
    path('', views.mail_server_view, name="mail-server-home"),
    path('revoke_outlook_oath', views.remove_outlook_auth, name="revoke-outlook-creds"),
    path('authorized', views.outlook_authorized, name='outlook-authorized'),
    path('outlook_webhook', views.webhook, name="outlook-webhook"),
    path('get_notification', views.get_notification, name="get_notification")
]
