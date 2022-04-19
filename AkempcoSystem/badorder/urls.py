from django.urls import path
from . import views

urlpatterns = [
    path('', views.bo_list, name='bo_list'),
    path('dt', views.BODTListView.as_view(), name='bo_dtlist'),
    path('create', views.BadOrderCreateView.as_view(), name='new_bo'),

    # pk = BadOrder pk
    path('<int:pk>/update', views.BadOrderUpdateView.as_view(), name='edit_bo'),
    path('<int:pk>/delete', views.delete_bo, name='delete_bo'),
    path('<int:pk>/print', views.PrintBODetailView.as_view(), name='print_bo'),
    path('<int:pk>/submit', views.submit_bo, name='submit_bo'),
    path('<int:pk>/approve', views.approve_bo, name='approve_bo'),
    path('<int:pk>/reject', views.reject_bo, name='reject_bo'),
    path('<int:pk>/action', views.set_action_taken, name='set_action_taken'),

    path('<int:pk>/products', views.BODetailView.as_view(), name='bo_products'),
    path('<int:pk>/products/add', views.BOProductCreateView.as_view(), name='bo_products_add'),

    # pk = BadOrderItem pk
    path('<int:pk>/products/delete', views.delete_bo_product, name='delete_bo_product'),
    path('<int:pk>/products/update', views.BOProductUpdateView.as_view(), name='update_bo_product'),
]