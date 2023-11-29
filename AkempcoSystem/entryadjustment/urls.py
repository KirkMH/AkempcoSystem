from django.urls import path
from . import views

urlpatterns = [
    path('', views.request_list, name='request_list'),
    path('dt', views.RequestDTListView.as_view(), name='request_dtlist'),
    path('new', views.RequestCreateView.as_view(), name='request_new'),
    path('<int:pk>/view', views.RequestDetailView.as_view(), name='request_view'),
    path('<int:pk>/approve', views.approve_request, name='request_approve'),
    path('<int:pk>/cancel', views.cancel_request, name='request_cancel'),
]