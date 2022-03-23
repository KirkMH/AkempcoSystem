from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.contrib import messages
from django.db.models import Q

from AkempcoSystem.decorators import user_is_allowed
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from fm.models import Product
from admin_area.models import Feature, Store
from fm.views import get_index, add_search_key
from .models import RequisitionVoucher, RV_Product
from .forms import RV_ProductForm


# for pagination
MAX_ITEMS_PER_PAGE = 10


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_STOCKS), name='dispatch')
class StockListView(ListView):
    model = Product
    context_object_name = "product"
    template_name = "stocks/stock_list.html"
    paginate_by = MAX_ITEMS_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # GM
        # - for approval
        # Storekeeper
        # - for receiving
        # WH
        # - for releasing
        userType = self.request.user.userdetail.userType
        count = 0
        if userType == 'General Manager':
            count = RequisitionVoucher.objects.filter(process_step=2).count()
        elif userType == 'Warehouse Staff':
            count = RequisitionVoucher.objects.filter(process_step=3).count()
        elif userType == 'Storekeeper':
            count = RequisitionVoucher.objects.filter(process_step=4).count()
        if count is None: count = 0
        context['count'] = count
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_STOCKS), name='dispatch')
class RVListView(ListView):
    model = RequisitionVoucher
    context_object_name = "rv"
    template_name = "stocks/requisition_voucher.html"
    paginate_by = MAX_ITEMS_PER_PAGE

    def get_queryset(self):
        # check if the user searched for something
        key = get_index(self.request, "table_search")
        object_list = self.model.objects.all()
        if key:
            object_list = object_list.filter(
                Q(pk__icontains=key)
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



@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_STOCKS), name='dispatch')
class RVProductCreateView(BSModalCreateView):
    template_name = 'stocks/rv_product_add.html'
    model = RV_Product
    form_class = RV_ProductForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"].fields["product"].queryset = Product.objects.filter(status='ACTIVE')
        return context

    def post(self, request, *args, **kwargs):
        my_form = self.form_class(self.request.POST)

        if my_form.is_valid():
            rv_prod = my_form.save(commit=False)
            rv = get_object_or_404(RequisitionVoucher, pk=self.kwargs['pk']) 
            new_qty = my_form.instance.quantity
            old_qty = rv.get_product_requested(my_form.instance.product)
            rv_prod.quantity = new_qty + old_qty
            rv_prod.rv = rv
            rv_prod.requested_by = self.request.user
            rv_prod.save()

        else:
            messages.error(self.request, 'Please fill-in all the required fields.')
        
        return redirect('rv_products', pk=self.kwargs['pk'])


@login_required
@user_is_allowed(Feature.TR_STOCKS)
def delete_rv_product(request, pk):
    rv_pk = 0
    try:
        rv = get_object_or_404(RV_Product, pk=pk)
        prod = rv.product.full_description
        rv_pk = rv.rv.pk
        rv.delete()
        messages.success(request, prod + " was removed from the requisition voucher.")
    except:
        messages.error(request, "There was an error removing the product from the Requisition Voucher.")
    return redirect('rv_products', pk=rv_pk)
    

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_STOCKS), name='dispatch')
class RVProductUpdateView(BSModalUpdateView):
    template_name = 'stocks/rv_product_add.html'
    model = RV_Product
    form_class = RV_ProductForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"].fields["product"].queryset = Product.objects.filter(status='ACTIVE')
        return context

    def get_success_url(self):
        rv_pk = self.object.rv.pk
        return reverse('rv_products', 
                        kwargs={'pk' : rv_pk})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_STOCKS), name='dispatch')
class PrintRVDetailView(DetailView):
    model = RequisitionVoucher
    context_object_name = 'rv'
    template_name = "stocks/rv_print.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = RV_Product.objects.filter(rv=self.object)
        context["akempco"] = Store.objects.all().first()
        return context


@login_required
@user_is_allowed(Feature.TR_STOCKS)
def submit_rv(request, pk):
    rv = get_object_or_404(RequisitionVoucher, pk=pk)
    if request.method == 'POST':
        rv.submit()
        messages.success(request, "Requisition Voucher was submitted for approval.")
    return redirect('rv_list')


@login_required
@user_is_allowed(Feature.TR_STOCKS)
def approve_rv(request, pk):
    this_rv = get_object_or_404(RequisitionVoucher, pk=pk)

    if request.method == 'POST':
        this_rv.approve(request.user)
        messages.success(request, "Requisition Voucher is now approved.")

    return redirect('rv_list')


@login_required
@user_is_allowed(Feature.TR_STOCKS)
def reject_rv(request, pk):
    this_rv = get_object_or_404(RequisitionVoucher, pk=pk)

    if request.method == 'POST':
        reason = request.POST.get('reject_reason', None)
        this_rv.reject(request.user, reason)
        messages.success(request, "Requisition Voucher is now rejected.")

    return redirect('rv_list')


@login_required
@user_is_allowed(Feature.TR_STOCKS)
def release_rv(request, pk):
    this_rv = get_object_or_404(RequisitionVoucher, pk=pk)

    if request.method == 'POST':
        this_rv.release(request.user)
        messages.success(request, "Requisition Voucher is now released.")

    return redirect('rv_list')


@login_required
@user_is_allowed(Feature.TR_STOCKS)
def receive_rv(request, pk):
    this_rv = get_object_or_404(RequisitionVoucher, pk=pk)

    if request.method == 'POST':
        this_rv.receive(request.user)
        messages.success(request, "Requisition Voucher is now received.")

    return redirect('rv_list')

    
@login_required()
@user_is_allowed(Feature.TR_STOCKS)
def clone_rv(request, pk):
    rv = get_object_or_404(RequisitionVoucher, pk=pk)
    new_rv = rv.clone(request.user)
    return redirect('rv_products', pk=new_rv.pk)