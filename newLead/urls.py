from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('newLead/', views.newLead_list, name='newLead-list'),
    path('newLead/<int:pk>', views.newLead_view, name='newLead-view'),
    path('newLead/search', views.newLead_search, name='newLead-search'),

]