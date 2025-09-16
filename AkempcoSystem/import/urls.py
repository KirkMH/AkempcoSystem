from django.urls import path
from . import views


urlpatterns = [
    path('', views.import_form, name='import_form'),
]