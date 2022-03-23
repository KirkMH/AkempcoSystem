from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_member_view, name='dashboard_member'),
]