from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.core.paginator import Paginator

from AkempcoSystem.decorators import user_is_allowed
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from admin_area.models import Feature
from fm.views import get_index, add_search_key
from fm.models import Supplier
from .models import PurchaseOrder


# for pagination
MAX_ITEMS_PER_PAGE = 10


# List of Suppliers to choose from
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class PurchaseSupplierListView(ListView):
    model = Supplier
    context_object_name = 'suppliers'
    template_name = "purchases/purchase_supplier.html"
    paginate_by = MAX_ITEMS_PER_PAGE

    def get_queryset(self):
        # check if the user searched for something
        key = get_index(self.request, "table_search")
        object_list = self.model.objects.all()
        if key:
            object_list = object_list.filter(
                Q(supplier_name__icontains=key)
            )
        return object_list


# PO List of selected supplier
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class PurchaseSupplierDetailView(DetailView):
    model = Supplier
    context_object_name = 'supplier'
    template_name = "purchases/po_list.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        supplier = Supplier.objects.get(pk=self.kwargs['pk'])
        context["po"] = PurchaseOrder.objects.filter(supplier=supplier)
        return context
    