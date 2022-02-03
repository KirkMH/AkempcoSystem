from django.urls import path
from . import views

urlpatterns = [
    path('creditor', views.CreditorListView.as_view(), name='cred_list'),
    path('creditor/new/', views.CreditorCreateView.as_view(), name='new_cred'),
    path('creditor/<int:pk>/edit/', views.CreditorUpdateView.as_view(), name='edit_cred'),

    path('pos', views.pos_view, name='pos'),
    path('pos/<int:pk>/add', views.add_to_cart, name='addToCart'),
    path('pos/<int:pk>/remove', views.remove_from_cart, name='removeFromCart'),

    path('pos/<int:pk>/search/product', views.product_search, name='pos_product_search'),
]