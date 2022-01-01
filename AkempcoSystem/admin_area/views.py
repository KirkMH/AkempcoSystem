from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Feature


def component_permissions(request):
    perms = request.user.userdetail.get_permissions()
    no_perms = []
    for f in Feature.LIST:
        if f[0] not in perms: no_perms.append(f[0])

    data = {
        'no_permissions': no_perms
    }
    return JsonResponse(data)


@login_required()
def dashboard_view(request):
    return render(request, 'dashboard.html')


def login_check(request):
    if request.user.is_authenticated:
        my_user = User.objects.get(pk=request.user.pk)
        if all([hasattr(my_user, 'userdetail'), my_user.userdetail.activated_at is not None]):
            return redirect('dashboard')
        else:
            return render(request, 'accounts/login_check.html')
    else:
        return redirect('login')