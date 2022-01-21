from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from fm.models import Product
from purchases.models import PurchaseOrder
from sales.models import Creditor
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
    # count how many critical level products exist
    critical_count = 0
    prods = Product.objects.filter(status='Active')
    for p in prods:
        if p.is_critical_level():
            critical_count = critical_count + 1

    # compute filled PO percentage
    open_count = PurchaseOrder.objects.filter(is_open=False).count()
    overall_count = PurchaseOrder.objects.all().count()
    if open_count is None: open_count = 0
    if overall_count is None: overall_count = 0
    filled_percent = 0
    if overall_count > 0:
        filled_percent = open_count / overall_count * 100

    # number of members
    member_count = Creditor.objects.filter(creditor_type='Member', active=True).count()

    # pass to template
    context = {
        'critical_count': critical_count,
        'filled_percent': int(filled_percent),
        'member_count': member_count
    }
    return render(request, 'dashboard.html', context)


def login_check(request):
    if request.user.is_authenticated:
        my_user = User.objects.get(pk=request.user.pk)
        if all([hasattr(my_user, 'userdetail'), my_user.userdetail.activated_at is not None]):
            return redirect('dashboard')
        else:
            return render(request, 'accounts/login_check.html')
    else:
        return redirect('login')