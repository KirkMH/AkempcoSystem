from django.shortcuts import render, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q
from django.core.paginator import Paginator

from AkempcoSystem.decorators import user_is_allowed
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from admin_area.models import Feature
from fm.views import get_index, add_search_key
from fm.models import Supplier
from .models import PurchaseOrder
from .forms import PurchaseOrderForm


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


# Create new PO
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class POCreateView(CreateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'purchases/po_new.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["supplier"] = Supplier.objects.get(pk=self.kwargs['pk'])
        return context
    
    def form_valid(self, form):
        form.instance.supplier = Supplier.objects.get(pk=self.kwargs.get('pk'))
        form.instance.prepared_by = self.request.user
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        # return reverse('ro_product_list', kwargs={'pk' : self.object.pk})
        return reverse('po_list', kwargs={'pk' : self.kwargs.get('pk')})

        
# Update PO details
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class POCreateView(UpdateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'purchases/po_new.html'
    pk_url_kwarg = 'po_pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["supplier"] = Supplier.objects.get(pk=self.kwargs['pk'])
        return context

    def get_success_url(self):
        # return reverse('ro_product_list', kwargs={'pk' : self.object.pk})
        return reverse('po_list', kwargs={'pk' : self.kwargs.get('pk')})
