from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.hashers import check_password # for overriding validation

from django_serverside_datatable.views import ServerSideDatatableView
from django.contrib.auth.models import User
from fm.views import get_index, add_search_key
from fm.models import Product
from AkempcoSystem.decorators import user_is_allowed
from admin_area.models import Feature, Store, UserDetail
from .models import *
from .forms import *


# used by pagination
MAX_ITEMS_PER_PAGE = 10


@login_required()
@user_is_allowed(Feature.TR_POS)
def creditor_search(request, pk):
    members = Creditor.members.all()
    groups = Creditor.groups.all()

    context = {
        'pk': pk,
        'members': members,
        'groups': groups
    }

    return render(request, 'sales/member_search.html', context)
    

@login_required()
@user_is_allowed(Feature.TR_POS)
def do_creditor_search(request):
    key = request.GET.get('key', '')
    members = list(Creditor.members.filter(name__icontains=key).values())
    groups = list(Creditor.groups.filter(name__icontains=key).values())
        
    data = {
        'members': members,
        'groups': groups,
    }
    return JsonResponse(data, safe=False)
    

@login_required()
@user_is_allowed(Feature.TR_POS)
def update_creditor(request, pk):
    sales = get_object_or_404(Sales, pk=pk)
    creditor = int(request.GET.get('creditor', 0))
    if creditor == 0:
        # Walk-in
        sales.set_customer(None)
    else:
        cred = get_object_or_404(Creditor, pk=creditor)
        sales.set_customer(cred)
    
    return JsonResponse(True, safe=False)


@login_required
@user_is_allowed(Feature.TR_POS)
def pos_view(request, pk=0):
    # check first if POS transactions are still allowed
    # not allowed when Z-Reading has been generated already
    if ZReading.validations.is_report_generated_today():
        # already generated, so this is an error
        messages.error(request, "A Z-Reading has already been generated for today. No further POS transactions are allowed this time.")
        return redirect('dashboard')

    # get the latest transaction in Sales
    sales = None
    try:
        if pk == 0:
            sales = Sales.objects.latest('transaction_datetime')
        else:
            sales = get_object_or_404(Sales, pk=pk)
    except:
        pass
    
    if sales == None or (sales and sales.status != 'WIP'):
        sales = Sales.objects.create()
    items = SalesItem.objects.filter(sales=sales)
    context = {
        'transaction': sales,
        'items': items,
    }
    return render(request, 'sales/pos.html', context)


@login_required()
@user_is_allowed(Feature.TR_POS)
def add_to_cart(request, pk):
    success = True
    barcode = request.GET.get('barcode', 0)
    qty = int(request.GET.get('qty', 0))

    sales = get_object_or_404(Sales, pk=pk)
    success, message = sales.add_product(barcode, qty)
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)

    data = {
        'success': success,
    }
    return JsonResponse(data, safe=False)


@login_required()
@user_is_allowed(Feature.TR_POS)
def remove_from_cart(request, pk):
    try:
        item = get_object_or_404(SalesItem, pk=pk)
        product = item.product
        item.delete()
        messages.success(request, "Removed " + product.full_description + ".")
    except:
        messages.error(request, "Cannot remove the item this time.")
    return redirect('pos')


@login_required()
@user_is_allowed(Feature.TR_POS)
def product_search(request, pk):
    transaction = get_object_or_404(Sales, pk=pk)

    return render(request, 'sales/product_search.html', {'transaction': transaction})

    
##########################
### CHECKOUT
##########################
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_BO), name='dispatch')
class PaymentDetailView(DetailView):
    model = Sales
    context_object_name = 'transaction'
    template_name = "sales/checkout.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = SalesPayment.objects.filter(sales=self.object)
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_POS), name='dispatch')
class SalesPaymentCreateView(BSModalCreateView):
    template_name = 'sales/receive_payment.html'
    model = SalesPayment
    form_class = SalesPaymentForm

    def post(self, request, *args, **kwargs):
        my_form = self.form_class(self.request.POST)

        if my_form.is_valid():
            pay_mode = my_form.save(commit=False)
            amount = pay_mode.amount
            sales = get_object_or_404(Sales, pk=self.kwargs['pk']) 
            if sales.customer == None and pay_mode.payment_mode == 'Charge':
                # this is a Walk-in customer; no charges
                messages.error(request, 'Charged sales are not allowed to walk-in customers.')
            elif sales.customer != None and pay_mode.payment_mode == 'Charge' and sales.customer.remaining_credit < pay_mode.amount:
                # insufficient balance
                messages.error(request, 'Insufficient remaining credit.')
            else:
                prev = SalesPayment.objects.filter(sales=sales, payment_mode=pay_mode.payment_mode)
                if prev:
                    prev = prev.first()
                    amount = amount + prev.amount
                    prev.delete()

                pay_mode.sales = sales
                pay_mode.amount = amount
                pay_mode.save()
                if sales.change > 0:
                    pay_mode.value = amount - sales.change
                else:
                    pay_mode.value = amount
                pay_mode.save()

        else:
            messages.error(self.request, 'Please fill-in all the required fields.')
            
        return redirect('checkout', pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('checkout', kwargs={'pk' : self.kwargs['pk']})


@login_required
@user_is_allowed(Feature.TR_POS)
def remove_payment(request, pk, payment_pk):
    try:
        payment = SalesPayment.objects.get(pk=payment_pk)
        payment.delete()
        messages.success(request, "Record was removed from the payment list.")
    except:
        messages.error(request, "There was an error removing the record from the payment list.")
    return redirect('checkout', pk=pk)


@login_required
@user_is_allowed(Feature.TR_POS)
def complete_checkout(request, pk):
    sales = Sales.objects.get(pk=pk)
    details = request.POST.get('details', '')       # retrieve details from the form
    details = None if details == '' else details    # make it null if there is no value
    si = sales.complete(request.user, details)
    return redirect('sales_invoice', pk=si)


@login_required
@user_is_allowed(Feature.TR_POS)
def sales_invoice(request, pk, for_transaction=0):
    transactional = False if for_transaction == 0 else True
    si = get_object_or_404(SalesInvoice, pk=pk)
    items = SalesItem.objects.filter(sales=si.sales)
    payments = SalesPayment.objects.filter(sales=si.sales)
    context = {
        'transaction': si,
        'items': items,
        'payments': payments,
        'for_transaction': transactional,
        'akempco': Store.objects.all().first()
    }
    return render(request, 'sales/sales_invoice.html', context)


@login_required
@user_is_allowed(Feature.TR_POS)
def open_receipt(request):
    pk = int(request.GET.get('si_number', 0))
    data = ""
    if SalesInvoice.objects.filter(pk=pk).exists():
        data = reverse('open_sales_invoice', kwargs={'pk': pk, 'for_transaction': 1})
    else:
        messages.error(request, 'Cannot find specified SI number.')
        data = reverse_lazy('pos')
    return JsonResponse(data, safe=False)


@login_required
@user_is_allowed(Feature.TR_POS)
def reprint_receipt(request, pk):
    data = "Re-printed"
    si = get_object_or_404(SalesInvoice, pk=pk)
    si.reprint(request.user)
    return JsonResponse(data, safe=False)
    

def validate_password(password):
    gm_list = User.objects.filter(userdetail__userType='General Manager')
    for gm in gm_list:
        valid = check_password(password, gm.password)
        if valid: 
            return gm
    return None


@login_required
@user_is_allowed(Feature.TR_POS)
def cancel_receipt(request, pk):
    pw = request.GET.get('password', '')

    # validate GM's password
    approver = validate_password(pw)
    valid = False
    
    if approver:
        si = get_object_or_404(SalesInvoice, pk=pk)
        si.cancel(request.user, approver)
        valid = True

    return JsonResponse(valid, safe=False)
    


@login_required
@user_is_allowed(Feature.TR_POS)
def password_for_discount(request):
    pw = request.GET.get('id_password', '')

    # validate GM's password
    approver = validate_password(pw)
    valid = True if approver else False

    return JsonResponse(valid, safe=False)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_POS), name='dispatch')
class SalesDiscountUpdateView(BSModalUpdateView):
    template_name = 'sales/discount_search.html'
    model = Sales
    form_class = DiscountForm

    def post(self, request, *args, **kwargs):
        my_form = self.form_class(self.request.POST)

        if my_form.is_valid():
            my_form.save()
            return super().post(request, args, kwargs)
        else:
            messages.error(self.request, "Please fill-in all the required fields.")
            return redirect('checkout', pk=self.kwargs['pk'])

    def get_success_url(self):
        print(self.object)
        self.object.apply_discount()
        return reverse('checkout', kwargs={'pk': self.object.pk})
    


@login_required
@user_is_allowed(Feature.TR_POS)
def reset_cart(request, pk):
    sales = get_object_or_404(Sales, pk=pk)
    sales.reset()

    data = True
    return JsonResponse(data, safe=False)
    

@login_required
@user_is_allowed(Feature.TR_POS)
def x_reading(request):
    xreading = Sales.reports.generate_xreading(request.user)
    return render(request, 'sales/x_reading.html', {'xreading' : xreading})


@login_required
@user_is_allowed(Feature.TR_POS)
def validate_gm_password(request):
    pw = request.GET.get('password', '')

    # validate GM's password
    approver = validate_password(pw)
    valid = False
    
    if approver:
        valid = True

    return JsonResponse(valid, safe=False)
    

@login_required
@user_is_allowed(Feature.TR_POS)
def z_reading(request):
    zreading = Sales.reports.generate_zreading(request.user)
    if zreading == False:
        # already generated; do not regenerate
        messages.error(request, "A Z-Reading has already been generated for today. No further POS transactions are allowed this time.")
        return redirect('dashboard')
    else:
        context = {
            'xreading' : zreading.xreading,
            'zreading' : zreading
        }
        return render(request, 'sales/z_reading.html', context)


@login_required
@user_is_allowed(Feature.TR_POS)
def copy_receipt(request, pk):
    si = int(request.GET.get('si_number', 0))
    data = False
    if SalesInvoice.objects.filter(pk=si).exists():
        sales = get_object_or_404(SalesInvoice, pk=si).sales
        this = get_object_or_404(Sales, pk=pk)
        if sales.clone(this):
            messages.success(request, 'Items in the specified SI has been copied successfully.')
            data = True
        else:
            messages.error(request, 'Failed to copy the specified SI.')

    else:
        messages.error(request, 'Cannot find specified SI number.')
        
    return JsonResponse(data, safe=False)