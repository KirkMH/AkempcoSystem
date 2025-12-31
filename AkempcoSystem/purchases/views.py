from django.forms.models import BaseModelForm
from django.shortcuts import redirect, reverse, get_object_or_404, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from datetime import datetime

from AkempcoSystem.decorators import user_is_allowed
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django_serverside_datatable.views import ServerSideDatatableView
from admin_area.models import Feature, Store
from admin_area.views import is_ajax
# from fm.views import get_index, add_search_key
from fm.models import Product, Supplier
from .models import PurchaseOrder, PO_Product, PO_PROCESS
from .forms import PurchaseOrderForm, PO_ProductForm


def get_po_approval_count(user):
    count = 0
    step = PO_PROCESS.which_step_this_user_is_in(user)
    if step > 0:
        count = PurchaseOrder.objects.filter(process_step=step).count()
    return count, step


# Loads a list of PO for approval if necessary
@login_required()
@user_is_allowed(Feature.TR_PURCHASES)
def purchasesupplier_list(request):
    template = ""
    count, step = get_po_approval_count(request.user)
    if count > 0 and request.user.userdetail.userType != 'Purchaser':
        return redirect('po_approval')
    else:
        return redirect('purchase_suppliers_all')


# List of Suppliers to choose from
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class POSupplierListView(ListView):
    model = Supplier
    context_object_name = 'objects'
    template_name = "purchases/purchase_supplier.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_po_approver"] = PO_PROCESS.is_po_approver(
            self.request.user)
        return context


# List of Suppliers to choose from
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class ApprovalListView(ListView):
    context_object_name = 'objects'
    template_name = "purchases/po_approval.html"

    def get_queryset(self):
        count, step = get_po_approval_count(self.request.user)
        object_list = None
        if count > 0:
            if self.request.user.userdetail.userType == 'Officer-In-Charge':
                object_list = PurchaseOrder.objects.filter(
                    process_step=step, category=self.request.user.userdetail.oic_for)
            elif self.request.user.userdetail.userType != 'Purchaser':
                object_list = PurchaseOrder.objects.filter(process_step=step)
        if object_list == None:
            object_list = PurchaseOrder.objects.all()
        return object_list


@login_required
@user_is_allowed(Feature.TR_PURCHASES)
def supplier_orders(request, pk):
    request.session['po_supplier_id'] = pk
    supplier = get_object_or_404(Supplier, pk=pk)
    return render(request, "purchases/po_list.html", {'supplier': supplier})


# PO List of selected supplier
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class PurchaseSupplierDTView(ServerSideDatatableView):

    def get(self, request, *args, **kwargs):
        pk = request.session.get('po_supplier_id', 0)
        supplier = get_object_or_404(Supplier, pk=pk)
        self.queryset = PurchaseOrder.objects.filter(supplier=supplier)
        self.columns = ['pk', 'po_date', 'category__category_description',
                        'item_count', 'total_po_amount', 'status']
        return super().get(request, *args, **kwargs)


# Create new PO
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class POCreateView(CreateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'purchases/po_create.html'

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
        return reverse('po_products', kwargs={'pk': self.object.pk})


# Update PO details
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class POUpdateView(UpdateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'purchases/po_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["supplier"] = self.object.supplier
        return context

    def get_success_url(self):
        return reverse('po_products', kwargs={'pk': self.object.pk})


# List of Products under PO
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class PODetailView(DetailView):
    model = PurchaseOrder
    context_object_name = 'po'
    template_name = "purchases/po_products.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object.is_receiving_now = False
        self.object.save()
        context["products"] = PO_Product.objects.filter(
            purchase_order=self.object)
        context["supplier"] = self.object.supplier
        context['for_approval'] = False
        userType = self.request.user.userdetail.userType
        # check if this user can approve this PO
        if (userType == self.object.get_user_type() and userType == 'Officer-In-Charge' and
                self.object.category == self.request.user.userdetail.oic_for) or \
                (userType != 'Officer-In-Charge' and userType != 'Purchaser' and
                 userType == self.object.get_user_type()):
            context['for_approval'] = True

        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class PODeleteView(DeleteView):
    model = PurchaseOrder

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        messages.success(self.request, "Purchase Order is now deleted.")
        return reverse('po_list', kwargs={'pk': self.object.supplier.pk})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class POProductCreateView(BSModalCreateView):
    template_name = 'purchases/product_add.html'
    model = PO_Product
    form_class = PO_ProductForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        po = get_object_or_404(PurchaseOrder, pk=self.kwargs['pk'])
        context["form"].fields["product"].queryset = Product.objects.filter(
            status='ACTIVE', suppliers=po.supplier, category=po.category)
        context['action'] = "Add"
        return context

    def form_valid(self, form):
        if not is_ajax(self.request):
            po_prod = form.save(commit=False)
            po = get_object_or_404(PurchaseOrder, pk=self.kwargs['pk'])
            ordered_quantity = form.instance.ordered_quantity
            prod_qty = po.get_product_ordered(form.instance.product)
            po_prod.ordered_quantity = ordered_quantity + prod_qty
            po_prod.purchase_order = po
            if po_prod.unit_price > 0:
                po_prod.is_price_originally_set = True
            po_prod.save()
            po_prod.compute_fields()
            po.fill_in_other_po_fields()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request, 'Please fill-in all the required fields.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('po_products', kwargs={'pk': self.kwargs['pk']})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class POProductUpdateView(BSModalUpdateView):
    template_name = 'purchases/product_add.html'
    model = PO_Product
    form_class = PO_ProductForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        po = self.object.purchase_order
        context["form"].fields["product"].queryset = Product.objects.filter(
            status='ACTIVE', suppliers=po.supplier, category=po.category)
        context['action'] = 'Edit'
        return context

    def get_success_url(self):
        return reverse('po_products',
                       kwargs={'pk': self.object.purchase_order.pk})

    def form_valid(self, form):
        prod = self.get_object().product.full_description
        self.object.compute_fields()
        self.object.purchase_order.fill_in_other_po_fields()
        return super().form_valid(form)

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        messages.error(
            self.request, 'Please fill-in all the required fields.')
        return super().form_invalid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class POProductDeleteView(BSModalDeleteView):
    model = PO_Product
    success_url = "/"

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        po = self.object.purchase_order
        po.fill_in_other_po_fields()
        return reverse('po_products',
                       kwargs={'pk': po.pk})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class PurchaseOrderDetailView(DetailView):
    model = PurchaseOrder
    context_object_name = 'po'
    template_name = "purchases/po_print.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["po_list"] = PO_Product.objects.filter(
            purchase_order=self.object)
        context["akempco"] = Store.objects.all().first()
        return context


@login_required
@user_is_allowed(Feature.TR_PURCHASES)
def submit_po(request, pk):
    this_po = get_object_or_404(PurchaseOrder, pk=pk)

    if request.method == 'POST':
        this_po.submit(request.user)
        messages.success(request, "Purchase Order was submitted successfully.")

    return redirect('po_list', pk=this_po.supplier.pk)


@login_required
@user_is_allowed(Feature.TR_PURCHASES)
def approve_po(request, pk):
    this_po = get_object_or_404(PurchaseOrder, pk=pk)

    if request.method == 'POST':
        this_po.approve(request.user)
        messages.success(request, "Purchase Order is now approved.")

    return redirect('po_list', pk=this_po.supplier.pk)


@login_required
@user_is_allowed(Feature.TR_PURCHASES)
def reject_po(request, pk):
    this_po = get_object_or_404(PurchaseOrder, pk=pk)

    if request.method == 'POST':
        reason = request.POST.get('reject_reason', None)
        this_po.reject(request.user, reason)
        messages.success(request, "Purchase Order is now rejected.")

    return redirect('po_list', pk=this_po.supplier.pk)


@login_required()
def select_product(request):
    ''' returns the inventory uom, supplier price of the selected product '''
    try:
        pk = request.GET.get('pk', 0)
        product = Product.objects.get(pk=pk)
        inv_uom = product.uom.uom_description

        # retrieve supplier price from PO_Product.unit_price
        po = PO_Product.objects.filter(product=product).filter(
            received_qty__gt=0).order_by('-id').first()
        supplier_price = 0
        if po:
            supplier_price = po.unit_price

        data = {
            'supplier_price': supplier_price,
            'inv_uom': inv_uom,
            'w_stock': product.warehouse_stocks,
            's_stock': product.store_stocks,
            'should_order': product.get_qty_should_order()
        }
        return JsonResponse(data, safe=False)

    except Product.DoesNotExist:
        return JsonResponse({'message': 'Cannot find product.'}, safe=False)


@login_required()
def load_data(request):
    key = request.GET['key']
    # filter to contain products under a specified supplier and category only
    supplier_id = int(request.GET.get('supplier_id', '0'))
    supplier = None
    if supplier_id > 0:
        supplier = get_object_or_404(Supplier, pk=supplier_id)
    prod_list = Product.objects.filter(
        Q(full_description__istartswith=key) |
        Q(barcode__istartswith=key)
    )
    if supplier:
        prod_list = prod_list.filter(suppliers=supplier)

    data = list(prod_list.values())
    return JsonResponse(data, safe=False)


##################################################
# FOR RECEIVING OF STOCKS
##################################################

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class PODetailViewReceiveStocks(DetailView):
    model = PurchaseOrder
    context_object_name = 'po'
    template_name = "purchases/receive_products.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.object.is_receiving_now:
            self.object.prepare_for_receiving()
        context["products"] = PO_Product.objects.filter(
            purchase_order=self.object)
        context["supplier"] = self.object.supplier
        return context


@login_required()
@user_is_allowed(Feature.TR_PURCHASES)
def update_receive_now(request, pk, item_pk):
    receive_now = int(request.POST.get('value', '0'))
    success = True
    try:
        po = PurchaseOrder.objects.get(pk=pk)
        po.is_receiving_now = True
        po.save()

        prod = PO_Product.objects.get(pk=item_pk)
        prod.receive_now = receive_now
        prod.save()
        print(prod.receive_now)
    except:
        success = False
    return JsonResponse(success, safe=False)


@login_required()
@user_is_allowed(Feature.TR_PURCHASES)
def update_unit_price(request, pk):
    unit_price = float(request.POST.get('value', '0'))
    success = True
    try:
        prod = PO_Product.objects.get(pk=pk)
        print(prod)
        prod.unit_price = unit_price
        prod.for_price_review = True
        prod.save()
    except:
        success = False
    return JsonResponse(success, safe=False)


@login_required()
@user_is_allowed(Feature.TR_PURCHASES)
def update_ref_no(request, pk):
    ref_no = request.POST.get('value', '')
    next_url = reverse('receive_stocks', kwargs={'pk': pk})
    try:
        po = PurchaseOrder.objects.get(pk=pk)
        po.reference_number = ref_no
        po.save()
    except:
        next_url = reverse('po_products', kwargs={'pk': pk})
    return JsonResponse(next_url, safe=False)


@login_required()
@user_is_allowed(Feature.TR_PURCHASES)
def update_price_review(request, pk):
    success = True
    try:
        prod = PO_Product.objects.get(pk=pk).product
        prod.for_price_review = True
        prod.save()
        print(prod.for_price_review)
    except:
        success = False
    print(success)
    return JsonResponse(success, safe=False)


@login_required()
@user_is_allowed(Feature.TR_PURCHASES)
def receive_stocks_save(request, pk):
    next_url = reverse('po_products', kwargs={'pk': pk})

    po = PurchaseOrder.objects.get(pk=pk)

    if po.are_all_prices_nonzero():
        po.receive_stocks(request.user)
        messages.success(request, "Stocks was received successfully.")
    else:
        messages.error(
            request, "Cannot receive stocks with zero prices. Please encode supplier price first.")
        next_url = reverse('receive_stocks', kwargs={'pk': pk})

    return JsonResponse(next_url, safe=False)


##################################################
# Undelivered Items: Backorder and Cancellation
##################################################

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class PODetailViewRR(DetailView):
    model = PurchaseOrder
    context_object_name = 'po'
    template_name = "purchases/rpt_receiving_print.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["po_list"] = PO_Product.objects.filter(
            purchase_order=self.object)
        context["akempco"] = Store.objects.all().first()
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class PODetailViewVR(DetailView):
    model = PurchaseOrder
    context_object_name = 'po'
    template_name = "purchases/rpt_variance_print.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["po_list"] = PO_Product.objects.filter(
            purchase_order=self.object)
        context["akempco"] = Store.objects.all().first()
        return context


##################################################
# Undelivered Items: Backorder and Cancellation
##################################################

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class POUndeliveredDetailView(DetailView):
    model = PurchaseOrder
    context_object_name = 'po'
    template_name = "purchases/undelivered_products.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = PO_Product.objects.filter(
            purchase_order=self.object)
        context["supplier"] = self.object.supplier
        return context


@login_required()
@user_is_allowed(Feature.TR_PURCHASES)
def split_backorder(request, pk):
    po = PurchaseOrder.objects.get(pk=pk)
    child_po = PurchaseOrder.objects.get(pk=pk)
    # clone PO details and add parent PO
    child_po.pk = None
    child_po.parent_po = pk
    child_po.po_date = datetime.now()
    child_po.save()
    new_po_pk = child_po.pk
    # split this PO
    po.split_to_backorder(child_po)

    data = {
        'success': True,
        'new_po_pk': new_po_pk,
        'next_url': 'show-modal'
    }
    return JsonResponse(data, safe=False)


@login_required()
@user_is_allowed(Feature.TR_PURCHASES)
def cancel_undelivered(request, pk):
    success = True
    next_url = reverse('po_products', kwargs={'pk': pk})

    try:
        po = PurchaseOrder.objects.get(pk=pk)
        po.cancel_undelivered()
        messages.success(
            request, "All undelivered items have been cancelled successfully.")

    except:
        success = False

    data = {
        'success': success,
        'next_url': next_url
    }
    return JsonResponse(data, safe=False)


@login_required()
@user_is_allowed(Feature.TR_PURCHASES)
def clone_po(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    new_po = po.clone(request.user)
    return redirect('po_products', pk=new_po.pk)
