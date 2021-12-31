from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from django.contrib import messages
from django.db.models import Q

from AkempcoSystem.decorators import user_is_allowed
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from fm.models import Product
from admin_area.models import Feature
from fm.views import get_index, add_search_key
from .models import RequisitionVoucher, RV_Product
from .forms import RV_ProductForm


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_STOCKS), name='dispatch')
class StockListView(ListView):
    model = Product
    context_object_name = "product"
    template_name = "stocks/stock_list.html"

    def get_queryset(self):
        # check if the user searched for something
        key = get_index(self.request, "table_search")
        object_list = self.model.objects.all()
        if key:
            object_list = object_list.filter(
                Q(full_description__icontains=key)
            )
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return add_search_key(self.request, context)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_STOCKS), name='dispatch')
class RVListView(ListView):
    model = RequisitionVoucher
    context_object_name = "rv"
    template_name = "stocks/requisition_voucher.html"

    def get_queryset(self):
        # check if the user searched for something
        key = get_index(self.request, "table_search")
        object_list = self.model.objects.all()
        if key:
            object_list = object_list.filter(
                Q(pk=key)
            )
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return add_search_key(self.request, context)


@login_required
@user_is_allowed(Feature.TR_STOCKS)
def create_new_rv(request):
    rv = RequisitionVoucher()
    rv.requested_by = request.user
    rv.save()
    return redirect('rv_products', pk=rv.pk)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_STOCKS), name='dispatch')
class RVDetailView(DetailView):
    model = RequisitionVoucher
    context_object_name = 'rv'
    template_name = "stocks/rv_products.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = RV_Product.objects.filter(rv=self.object)
        return context



@login_required
@user_is_allowed(Feature.TR_STOCKS)
def delete_rv(request, pk):
    try:
        rv = get_object_or_404(RequisitionVoucher, pk=pk)
        rv.delete()
        messages.success(request, "Requisition Voucher is now deleted.")
        return redirect('rv_list')
    except:
        messages.error(request, "There was an error deleting the Requisition Voucher.")
        return redirect('rv_products', pk=pk)


class RVProductCreateView(BSModalCreateView):
    template_name = 'stocks/rv_product_add.html'
    model = RV_Product
    form_class = RV_ProductForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"].fields["product"].queryset = Product.objects.filter(status='ACTIVE')
        return context

    def get_success_url(self):
        return reverse('rv_products', kwargs={'pk' : self.kwargs['pk']})

    def form_valid(self, form):
        form.instance.rv = get_object_or_404(RequisitionVoucher, pk=self.kwargs['pk']) 
        form.instance.requested_by = self.request.user
        form.save()
        return super().form_valid(form)