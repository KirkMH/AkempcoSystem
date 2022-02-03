from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from fm.views import get_index, add_search_key
from fm.models import Product
from AkempcoSystem.decorators import user_is_allowed
from admin_area.models import Feature
from .models import *
from .forms import *
from .models import Sales, SalesItem


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
        

@login_required
@user_is_allowed(Feature.TR_POS)
def pos_view(request):
    # get the latest transaction in Sales
    sales = None
    try:
        sales = Sales.objects.latest('transaction_datetime')
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