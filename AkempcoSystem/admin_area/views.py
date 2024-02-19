from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Sum

from dateutil.relativedelta import relativedelta
from django.utils import timezone

from fm.models import Product, Supplier
from sales.models import XReading
from purchases.models import PurchaseOrder
from member.models import Creditor
from .models import Feature, UserType


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def component_permissions(request):
    perms = request.user.userdetail.get_permissions()
    no_perms = []
    for f in Feature.LIST:
        if f[0] not in perms:
            no_perms.append(f[0])

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
    if open_count is None:
        open_count = 0
    if overall_count is None:
        overall_count = 0
    filled_percent = 0
    if overall_count > 0:
        filled_percent = open_count / overall_count * 100

    # number of members
    member_count = Creditor.objects.filter(active=True).count()

    # number of suppliers
    supplier_count = Supplier.objects.filter(status='Active').count()

    # get the month six months ago
    six_months_ago = timezone.now() - relativedelta(months=5)

    # calculate monthly sales
    monthly_sales = []
    displays = []
    for i in range(6):
        month = six_months_ago + relativedelta(months=i)
        total = 0
        total_sales = XReading.objects.filter(
            created_at__month=month.month, created_at__year=month.year,
            zreading__isnull=False).aggregate(
            total_sales=Sum('total_sales'))['total_sales']
        month_display = month.strftime('%B %Y')
        if total_sales is not None:
            total = float(total_sales)
        monthly_sales.append(total)
        displays.append(month_display)

    # pass to template
    context = {
        'critical_count': critical_count,
        'filled_percent': int(filled_percent),
        'member_count': member_count,
        'supplier_count': supplier_count,
        'monthly_sales': monthly_sales,
        'displays': displays
    }
    return render(request, 'dashboard.html', context)


def login_check(request):
    if request.user.is_authenticated:
        my_user = User.objects.get(pk=request.user.pk)
        if hasattr(my_user, 'userdetail') and my_user.userdetail.activated_at is not None:
            if my_user.userdetail.userType == UserType.CREDITOR:
                return redirect('dashboard_member')
            else:
                return redirect('dashboard')
        else:
            return render(request, 'accounts/login_check.html')
    else:
        return redirect('login')
