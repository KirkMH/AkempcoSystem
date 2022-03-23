from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('dashboard', views.dashboard_view, name='dashboard'),
    path('', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/check', views.login_check, name='login_check'),

    path('ajax/component_permissions', views.component_permissions, name='component_permissions'),
]