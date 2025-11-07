from django.urls import path
from . import views

app_name = 'base'

urlpatterns = [
    path('', views.events_list, name='events_list'),
    path('events/<int:eventID>/', views.event_detail, name='event_detail'),
]
