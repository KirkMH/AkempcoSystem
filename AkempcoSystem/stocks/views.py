import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.contrib import messages
from django.db.models import Q
from django_serverside_datatable.views import ServerSideDatatableView
from django.contrib.messages.views import SuccessMessageMixin

from AkempcoSystem.decorators import user_is_allowed
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from admin_area.views import is_ajax
from fm.models import Product, Category
from admin_area.models import Feature, Store
from reports.models import InventoryCountItem
from .models import RequisitionVoucher, RV_Product, StockAdjustment
from .forms import RV_ProductForm, StockAdjustmentForm


@login_required
@user_is_allowed(Feature.TR_STOCKS)
def stock_list(request):
    userType = request.user.userdetail.userType
    count = 0
    if userType == 'General Manager':
        count = RequisitionVoucher.objects.filter(process_step=2).count()
    elif userType == 'Warehouse Staff':
        count = RequisitionVoucher.objects.filter(process_step=3).count()
    elif userType == 'Storekeeper':
        count = RequisitionVoucher.objects.filter(process_step=4).count()
    if count is None:
        count = 0

    return render(request, "stocks/stock_list.html", {'count': count})


@method_decorator(login_required, name='dispatch')
class StockDTListView(ServerSideDatatableView):
    model = Product
    columns = ['pk', 'barcode', 'full_description', 'warehouse_stocks', 'store_stocks',
               'total_stocks', 'reorder_point', 'category__category_description']


@login_required
@user_is_allowed(Feature.TR_STOCKS)
def rv_list(request):
    return render(request, "stocks/requisition_voucher.html")


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_STOCKS), name='dispatch')
class RVDTListView(ServerSideDatatableView):
    model = RequisitionVoucher
    columns = ['pk', 'item_count', 'requested_at', 'status', 'process_step']


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
        messages.error(
            request, "There was an error deleting the Requisition Voucher.")
        return redirect('rv_products', pk=pk)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_STOCKS), name='dispatch')
class RVProductCreateView(BSModalCreateView):
    template_name = 'stocks/rv_product_add.html'
    model = RV_Product
    form_class = RV_ProductForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"].fields["product"].queryset = Product.objects.filter(
            status='ACTIVE')
        return context

    def form_valid(self, form):
        if not is_ajax(self.request):
            rv_prod = form.save(commit=False)
            rv = get_object_or_404(RequisitionVoucher, pk=self.kwargs['pk'])
            w_qty = rv_prod.product.warehouse_stocks
            new_qty = form.instance.quantity
            old_qty = rv.get_product_requested(form.instance.product)
            rv_prod.quantity = new_qty + old_qty
            if rv_prod.quantity > w_qty:
                rv_prod.quantity = w_qty
            rv_prod.rv = rv
            rv_prod.requested_by = self.request.user
            rv_prod.save()
            rv.set_item_count()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, 'Please fill-in all the required fields.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('rv_products', kwargs={'pk': self.kwargs['pk']})


@login_required
@user_is_allowed(Feature.TR_STOCKS)
def delete_rv_product(request, pk):
    rv_pk = 0
    try:
        rv = get_object_or_404(RV_Product, pk=pk)
        rv_pk = rv.rv.pk
        prod = rv.product.full_description
        rv.rv.set_item_count()
        rv.delete()
        messages.success(
            request, prod + " was removed from the requisition voucher.")
    except:
        messages.error(
            request, "There was an error removing the product from the Requisition Voucher.")
    return redirect('rv_products', pk=rv_pk)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_STOCKS), name='dispatch')
class RVProductUpdateView(BSModalUpdateView):
    template_name = 'stocks/rv_product_add.html'
    model = RV_Product
    form_class = RV_ProductForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"].fields["product"].queryset = Product.objects.filter(
            status='ACTIVE')
        return context

    def get_success_url(self):
        self.object.rv.set_item_count()
        rv_pk = self.object.rv.pk
        return reverse('rv_products',
                       kwargs={'pk': rv_pk})


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
        messages.success(
            request, "Requisition Voucher was submitted for approval.")
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


@login_required
@user_is_allowed(Feature.TR_STOCKADJ)
def adjustment_list(request):
    return render(request, "stocks/stock_adjustment.html")


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_STOCKADJ), name='dispatch')
class StockAdjustmentDTListView(ServerSideDatatableView):
    model = StockAdjustment
    columns = ['pk', 'product__full_description', 'quantity',
               'location', 'reason', 'created_at', 'status']


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_STOCKADJ), name='dispatch')
class StockAdjustmentCreateView(SuccessMessageMixin, CreateView):
    model = StockAdjustment
    form_class = StockAdjustmentForm
    template_name = 'stocks/stock_adjustment_new.html'
    success_message = "New stock adjustment request created."
    success_url = reverse_lazy('adjustment_list')

    def form_valid(self, form):
        adjustment = form.save(commit=False)
        form.instance.created_by = self.request.user
        form.save()
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_STOCKADJ), name='dispatch')
class StockAdjustmentDetailView(DetailView):
    model = StockAdjustment
    template_name = "stocks/stock_adjustment_view.html"
    context_object_name = 'adjustment'


@login_required
@user_is_allowed(Feature.TR_STOCKADJ)
def approve_adjustment(request, pk):
    adjustment = get_object_or_404(StockAdjustment, pk=pk)
    adjustment.approve(request.user)
    messages.success(request, "Stock adjustment was approved.")
    return redirect('adjustment_list')


@login_required
@user_is_allowed(Feature.TR_STOCKADJ)
def cancel_adjustment(request, pk):
    adjustment = get_object_or_404(StockAdjustment, pk=pk)
    adjustment.cancel(request.user)
    messages.success(request, "Stock adjustment was cancelled.")
    return redirect('adjustment_list')


def _generate_inventory_csv(location, cycle, report_id):
    # Create the HttpResponse object with the appropriate CSV header.
    filename = f"{location.lower()}-stocks.csv"
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    )

    writer = csv.writer(response)
    writer.writerow(['ID (Do not modify)', 'Barcode',
                    'Description', 'Physical Count'])

    # Fetch all active categories to maintain order and include empty ones
    categories = Category.objects.filter(status='ACTIVE')
    category_map = {c.pk: c for c in categories}

    # Fetch products efficiently
    products_by_category = {}
    
    if cycle == 1:
        # For cycle 1, fetch all active products
        products_qs = Product.objects.filter(
            status='ACTIVE'
        ).select_related('category').order_by('full_description')
    else:
        # For other cycles, fetch products with variances from the previous cycle
        prod_ids = InventoryCountItem.objects.filter(
            cycle=cycle-1, 
            location=location, 
            report_id=report_id
        ).exclude(variance=0).values_list('product', flat=True)
        
        products_qs = Product.objects.filter(
            pk__in=prod_ids
        ).select_related('category').order_by('full_description')

    # Group products by category in memory
    for prod in products_qs:
        # Only include products belonging to active categories
        if prod.category_id in category_map:
            products_by_category.setdefault(prod.category_id, []).append(prod)

    # Write to CSV
    for cat in categories:
        writer.writerow(['', '', '', ''])
        writer.writerow([cat.category_description, '', '', ''])
        
        cat_products = products_by_category.get(cat.pk, [])
        for prod in cat_products:
            writer.writerow(
                [prod.pk, "'" + str(prod.barcode), prod.full_description, ''])

    return response


@login_required
def inventory_count_form_store(request):
    cycle = int(request.GET.get('cycle', 1))
    report_id = request.GET.get('report_id', None)
    return _generate_inventory_csv("Store", cycle, report_id)


@login_required
def inventory_count_form_warehouse(request):
    cycle = int(request.GET.get('cycle', 1))
    report_id = request.GET.get('report_id', None)
    return _generate_inventory_csv("Warehouse", cycle, report_id)
