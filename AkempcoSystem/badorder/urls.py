from django.urls import path
from . import views

urlpatterns = [
    path('', views.BOListView.as_view(), name='bo_list'),
    path('create', views.BadOrderCreateView.as_view(), name='new_bo'),
    path('<int:pk>/update', views.BadOrderUpdateView.as_view(), name='edit_bo'),
]