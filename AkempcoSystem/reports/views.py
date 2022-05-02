from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django_serverside_datatable.views import ServerSideDatatableView

from fm.views import get_index, add_search_key

from AkempcoSystem.decorators import user_is_allowed
from admin_area.models import Feature, Store
from fm.models import Product
from stocks.models import ProductHistory


@login_required
@user_is_allowed(Feature.RP_PRODHIST)
def product_list_history(request):
    return render(request,"reports/product_list_hist.html")

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.RP_PRODHIST), name='dispatch')
class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'reports/product_history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["akempco"] = Store.objects.all().first()
        context["w_history"] = ProductHistory.for_warehouse.filter(product=self.object)[:50]
        context["s_history"] = ProductHistory.for_store.filter(product=self.object)[:50]
        return context
    

@login_required
@user_is_allowed(Feature.RP_PRODHIST)
def product_warehouse_history(request, pk):
    akempco = Store.objects.all().first()
    context = {
        'akempco': akempco,
        'product': get_object_or_404(Product, pk=pk)
    }
    return render(request, 'reports/product_history_warehouse.html', context)    
    
@method_decorator(login_required, name='dispatch')
class ProductWarehouseDTView(ServerSideDatatableView):
    
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk', 0)
        product = get_object_or_404(Product, pk=pk)
        self.queryset = ProductHistory.for_warehouse.filter(product=product)
        self.columns = ['pk', 'performed_on', 'quantity', 'remarks', 'performed_by__first_name', 'performed_by__last_name', 'balance']
        return super().get(request, *args, **kwargs)
     
    

@login_required
@user_is_allowed(Feature.RP_PRODHIST)
def product_store_history(request, pk):
    akempco = Store.objects.all().first()
    context = {
        'akempco': akempco,
        'product': get_object_or_404(Product, pk=pk)
    }
    return render(request, 'reports/product_history_store.html', context)    
    
@method_decorator(login_required, name='dispatch')
class ProductStoreDTView(ServerSideDatatableView):
    
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk', 0)
        product = get_object_or_404(Product, pk=pk)
        self.queryset = ProductHistory.for_store.filter(product=product)
        self.columns = ['pk', 'performed_on', 'quantity', 'remarks', 'performed_by__first_name', 'performed_by__last_name', 'balance']
        return super().get(request, *args, **kwargs)
     