from django.urls import path
from . import views


urlpatterns = [
    path('uom', views.UomListView.as_view(), name='uom_list'),
    path('uom/new/', views.UomCreateView.as_view(), name='new_uom'),
    path('uom/<int:pk>/edit/', views.UomUpdateView.as_view(), name='edit_uom'),
]