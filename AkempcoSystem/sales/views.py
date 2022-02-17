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

from fm.views import get_index, add_search_key
from fm.models import Product
from AkempcoSystem.decorators import user_is_allowed
from admin_area.models import Feature, Store
from .models import *
from .forms import *
from .models import Sales, SalesItem, SalesPayment


# used by pagination
MAX_ITEMS_PER_PAGE = 10


################################
#   Creditor FM
################################

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_CREDITOR), name='dispatch')
class CreditorListView(ListView):
    model = Creditor
    context_object_name = 'creditors'
    template_name = "sales/creditor_list.html"
    paginate_by = MAX_ITEMS_PER_PAGE

    def get_queryset(self):
        # check if the user searched for something
        key = get_index(self.request, "table_search")
        object_list = self.model.objects.all()
        if key:
            object_list = object_list.filter(
                Q(name__icontains=key) |
                Q(address__icontains=key) |
                Q(creditor_type__icontains=key) |
                Q(credit_limit__icontains=key) |
                Q(status__icontains=key)
            )
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return add_search_key(self.request, context)    
    
    
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_CREDITOR), name='dispatch')
class CreditorCreateView(CreateView):
    model = Creditor
    form_class = NewCreditorForm
    template_name = 'sales/creditor_form.html'

    def post(self, request, *args, **kwargs):
        form = NewCreditorForm(request.POST)
        if form.is_valid():
            cred = form.save()
            cred.save()
            messages.success(request, cred.name + " was created successfully.")
            if "another" in request.POST:
                return redirect('new_cred')
            else:
                return redirect('cred_list')
        
        else:
            return render(request, 'sales/creditor_form.html', {'form': form})
        

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_CREDITOR), name='dispatch')
class CreditorUpdateView(SuccessMessageMixin, UpdateView):
    model = Creditor
    context_object_name = 'creditor'
    form_class = UpdateCreditorForm
    template_name = "sales/creditor_form.html"
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('cred_list')
    success_message = "%(name)s was updated successfully."


@login_required()
@user_is_allowed(Feature.TR_POS)
def creditor_search(request, pk):
    members = Creditor.members.all()
    groups = Creditor.groups.all()

    print(f"members: {members}")
    print(f"groups: {groups}")

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
    # try:
    sales = Sales.objects.get(pk=pk)
    print(sales)
    si = sales.complete(request.user)
    # messages.success(request, 'Checkout completed for SI# ' + si + '.')
    return redirect('sales_invoice', pk=si)
    # except:
    #     messages.error(request, "There was an error completing the checkout operation.")
    #     return redirect('checkout', pk=pk)


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
        print('No match')
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
    