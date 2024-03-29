"""AkempcoSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views 

urlpatterns = [
    path('admin/login/', auth_views.LoginView.as_view(template_name='accounts/login-admin.html'), name='login_admin'),
    path('admin/', admin.site.urls),
    path('', include('admin_area.urls')),
    path('fm/', include('fm.urls')),
    path('purchases/', include('purchases.urls')),
    path('pricing/', include('pricing.urls')),
    path('stocks/', include('stocks.urls')),
    path('entryadj/', include('entryadjustment.urls')),
    path('reports/', include('reports.urls')),
    path('sales/', include('sales.urls')),
    path('bo/', include('badorder.urls')),
    path('member/', include('member.urls')),
]
