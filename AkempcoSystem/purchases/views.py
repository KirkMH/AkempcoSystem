from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.core.paginator import Paginator
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView, BSModalDeleteView
from django.http import JsonResponse
from datetime import datetime

from AkempcoSystem.decorators import user_is_allowed
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from admin_area.models import Feature, Store
from fm.views import get_index, add_search_key
from fm.models import Product, Supplier
from .models import PurchaseOrder, PO_Product
from .forms import PurchaseOrderForm, PO_ProductForm


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
        context["po"] = PurchaseOrder.objects.filter(supplier=self.object)
        return context


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
        return reverse('po_products', kwargs={'pk' : self.object.pk})

        
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
        return reverse('po_products', kwargs={'pk' : self.object.pk})


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
        context["products"] = PO_Product.objects.filter(purchase_order=self.object)
        context["supplier"] = self.object.supplier
        return context



@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class PODeleteView(DeleteView):
    model = PurchaseOrder
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
        
    def get_success_url(self):
        return reverse('po_list', kwargs={'pk' : self.object.supplier.pk})



@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class POProductCreateView(BSModalCreateView):
    template_name = 'purchases/product_add.html'
    model = PO_Product
    form_class = PO_ProductForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        po = get_object_or_404(PurchaseOrder, pk=self.kwargs['pk'])
        context["form"].fields["product"].queryset = Product.objects.filter(status='ACTIVE', suppliers=po.supplier, category=po.category)
        return context

    def get_success_url(self):
        return reverse('po_products', kwargs={'pk' : self.kwargs['pk']})

    def form_valid(self, form):
        form.instance.purchase_order = get_object_or_404(PurchaseOrder, pk=self.kwargs['pk'])
        # messages.success(self.request, form.instance.product.full_description + ' was added.')  
        return super().form_valid(form)
    

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class POProductUpdateView(BSModalUpdateView):
    template_name = 'purchases/product_add.html'
    model = PO_Product
    form_class = PO_ProductForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        po = get_object_or_404(PurchaseOrder, pk=self.kwargs['pk'])
        context["form"].fields["product"].queryset = Product.objects.filter(status='ACTIVE', suppliers=po.supplier, category=po.category)
        return context

    def get_object(self):
        item_pk = self.kwargs['item_pk']
        return PO_Product.objects.get(pk=item_pk)

    def get_success_url(self):
        return reverse('po_products', 
                        kwargs={'pk' : self.kwargs['pk']})

    def form_valid(self, form):
        prod = self.get_object().product.full_description
        # messages.success(self.request, prod + ' was updated.')  
        return super().form_valid(form)
    

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class POProductDeleteView(BSModalDeleteView):
    model = PO_Product
    success_url = "/"
    # success_message = "Successfully removed."

    def get_object(self):
        item_pk = self.kwargs['item_pk']
        return PO_Product.objects.get(pk=item_pk)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('po_products', 
                        kwargs={'pk' : self.kwargs['pk']})



@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class PurchaseOrderDetailView(DetailView):
    model = PurchaseOrder
    context_object_name = 'po'
    template_name = "purchases/po_print.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["po_list"] = PO_Product.objects.filter(purchase_order=self.object)
        context["akempco"] = Store.objects.all().first()
        return context


@login_required
@user_is_allowed(Feature.TR_PURCHASES)
def submit_po(request, pk):
    this_po = get_object_or_404(PurchaseOrder, pk=pk)

    if request.method == 'POST':
        print(request.user)
        this_po.submit(request.user)

    return redirect('po_list', pk=this_po.supplier.pk)


@login_required
@user_is_allowed(Feature.TR_PURCHASES)
def approve_po(request, pk):
    this_po = get_object_or_404(PurchaseOrder, pk=pk)

    if request.method == 'POST':
        this_po.approve(request.user)

    return redirect('po_list', pk=this_po.supplier.pk)


@login_required
@user_is_allowed(Feature.TR_PURCHASES)
def reject_po(request, pk):
    this_po = get_object_or_404(PurchaseOrder, pk=pk)

    if request.method == 'POST':
        reason = request.POST.get('reject_reason', None)
        this_po.reject(request.user, reason)

    return redirect('po_list', pk=this_po.supplier.pk)


@login_required()
def select_product(request):
    ''' returns the inventory uom, supplier price of the selected product '''
    try:
        pk = request.GET.get('pk', 0)
        product = Product.objects.get(pk=pk)
        inv_uom = product.uom.uom_description

        # retrieve supplier price from PO_Product.unit_price
        po = PO_Product.objects.filter(product=product).filter(received_qty__gt=0).order_by('-id').first()
        supplier_price = 0
        if po:
            supplier_price = po.unit_price

        data = {
            'supplier_price': supplier_price,
            'inv_uom': inv_uom
        }

        return JsonResponse(data, safe=False)

    except Product.DoesNotExist:
        return JsonResponse({'message': 'Cannot find product.'}, safe=False)


@login_required()
def load_data(request):
    key = request.GET['key']
    # filter to contain products under a specified supplier and category only
    supplier_id = request.GET['supplier_id']
    supplier = get_object_or_404(Supplier, pk=supplier_id)
    data = list(Product.objects.filter(
            Q(suppliers=supplier) &
            Q(full_description__istartswith=key) |
            Q(barcode__istartswith=key)
        )[:50].values())
    return JsonResponse(data, safe=False)


##################################################
#### FOR RECEIVING OF STOCKS
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
        context["products"] = PO_Product.objects.filter(purchase_order=self.object)
        context["supplier"] = self.object.supplier
        return context


@login_required()
@user_is_allowed(Feature.TR_PURCHASES)
def update_receive_now(request, pk):
    item_pk = int(request.POST.get('item_pk', '0'))
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
    item_pk = int(request.POST.get('item_pk', '0'))
    unit_price = float(request.POST.get('value', '0'))
    success = True
    try:
        prod = PO_Product.objects.get(pk=item_pk)
        prod.unit_price = unit_price
        prod.set_for_price_review()
        prod.save()
    except:
        success = False
    return JsonResponse(success, safe=False)


@login_required()
@user_is_allowed(Feature.TR_PURCHASES)
def update_ref_no(request, pk):
    ref_no = request.POST.get('value', '')
    next_url = reverse('receive_stocks', kwargs={'pk' : pk})
    try:
        po = PurchaseOrder.objects.get(pk=pk)
        po.reference_number = ref_no
        po.save()
    except:
        next_url = reverse('po_products', kwargs={'pk' : pk})
    return JsonResponse(next_url, safe=False)


@login_required()
@user_is_allowed(Feature.TR_PURCHASES)
def receive_stocks_save(request, pk):
    next_url = reverse('po_products', kwargs={'pk' : pk})

    try:
        po = PurchaseOrder.objects.get(pk=pk)
        po.receive_stocks(request.user)
    except:
        next_url = reverse('receive_stocks', kwargs={'pk' : pk})

    print(next_url)
    return JsonResponse(next_url, safe=False)