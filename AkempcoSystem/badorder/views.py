from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q

from fm.views import get_index, add_search_key
from AkempcoSystem.decorators import user_is_allowed
from admin_area.models import Feature, Store
from .models import *
from .forms import *


# used by pagination
MAX_ITEMS_PER_PAGE = 10


################################
#   Creditor FM
################################

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_BO), name='dispatch')
class BOListView(ListView):
    model = BadOrder
    context_object_name = 'badorders'
    template_name = "badorder/bo_list.html"
    paginate_by = MAX_ITEMS_PER_PAGE

    def get_queryset(self):
        # check if the user searched for something
        key = get_index(self.request, "table_search")
        object_list = self.model.objects.all()
        if key:
            key = key.lower()
            loc = None
            if key == 'warehouse':
                loc = True
            elif key == 'store':
                loc = False
            if loc is not None:
                object_list = object_list.filter(
                    Q(supplier__supplier_name__icontains=key) |
                    Q(in_warehouse=loc)
                )
            else:
                object_list = object_list.filter(
                    Q(supplier__supplier_name__icontains=key)
                )
        if self.request.user.userdetail.userType == 'Warehouse Staff':
            object_list = object_list.filter(in_warehouse=True)
        elif self.request.user.userdetail.userType == 'Storekeeper':
            object_list = object_list.filter(in_warehouse=False)
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return add_search_key(self.request, context)    
    
    
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_BO), name='dispatch')
class BadOrderCreateView(CreateView):
    model = BadOrder
    form_class = BadOrderForm
    template_name = 'badorder/bo_form.html'

    def post(self, request, *args, **kwargs):
        form = BadOrderForm(request.POST)
        if form.is_valid():
            bo = form.save(commit=False)
            bo.reported_by = self.request.user
            bo.save()
            messages.success(request, "The bad order record was created successfully.")
            return redirect('bo_products', pk=bo.pk)
        
        else:
            return render(request, 'badorder/bo_form.html', {'form': form})
        

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_BO), name='dispatch')
class BadOrderUpdateView(SuccessMessageMixin, UpdateView):
    model = BadOrder
    context_object_name = 'badorder'
    form_class = BadOrderForm
    template_name = "badorder/bo_form.html"
    pk_url_kwarg = 'pk'
    success_message = "The bad order record was updated successfully."

    def get_success_url(self):
        return reverse('bo_products', kwargs={'pk' : self.object.pk})



@login_required
@user_is_allowed(Feature.TR_BO)
def delete_bo(request, pk):
    try:
        rv = get_object_or_404(BadOrder, pk=pk)
        rv.delete()
        messages.success(request, "Bad order record is now deleted.")
        return redirect('bo_list')
    except:
        messages.error(request, "There was an error deleting the bad order record. Please try again.")
        return redirect('bo_products', pk=pk)

    

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_BO), name='dispatch')
class BODetailView(DetailView):
    model = BadOrder
    context_object_name = 'badorder'
    template_name = "badorder/bo_products.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = BadOrderItem.objects.filter(bad_order=self.object)
        return context



@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_BO), name='dispatch')
class BOProductCreateView(BSModalCreateView):
    template_name = 'badorder/bo_product_add.html'
    model = BadOrderItem
    form_class = BadOrderItemForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bo = get_object_or_404(BadOrder, pk=self.kwargs['pk']) 
        context["form"].fields["product"].queryset = Product.objects.filter(suppliers=bo.supplier, status='ACTIVE')
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST)

        if form.is_valid():
            bo = get_object_or_404(BadOrder, pk=self.kwargs['pk']) 
            new_qty = form.instance.quantity
            old_qty = bo.get_product_qty(form.instance.product)
            form.instance.quantity = new_qty + old_qty
            form.instance.bad_order = bo
            form.instance.requested_by = self.request.user
            form.save()

        else:
            messages.error(self.request, 'Please fill-in all the required fields.')
            
        return redirect('bo_products', pk=self.kwargs['pk'])



@login_required
@user_is_allowed(Feature.TR_BO)
def delete_bo_product(request, pk):
    bo_pk = 0
    try:
        boi = get_object_or_404(BadOrderItem, pk=pk)
        bo_pk = boi.bad_order.pk
        prod = boi.product.full_description
        boi.delete()
        messages.success(request, prod + " was removed from the bad order record.")
    except:
        messages.error(request, "There was an error removing the product from the bad order record.")
    return redirect('bo_products', pk=bo_pk)
    

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_BO), name='dispatch')
class BOProductUpdateView(BSModalUpdateView):
    template_name = 'badorder/bo_product_add.html'
    model = BadOrderItem
    form_class = BadOrderItemForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"].fields["product"].queryset = Product.objects.filter(status='ACTIVE')
        return context

    def get_success_url(self):
        bo_pk = self.object.bad_order.pk
        return reverse('bo_products', 
                        kwargs={'pk' : bo_pk})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_BO), name='dispatch')
class PrintBODetailView(DetailView):
    model = BadOrder
    context_object_name = 'badorder'
    template_name = "badorder/bo_print.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = BadOrderItem.objects.filter(bad_order=self.object)
        context["akempco"] = Store.objects.all().first()
        return context


@login_required
@user_is_allowed(Feature.TR_BO)
def submit_bo(request, pk):
    bo = get_object_or_404(BadOrder, pk=pk)
    if request.method == 'POST':
        if bo.submit(request.user):
            messages.success(request, "Bad order record was submitted for approval.")
        else:
            messages.error(request, "There was an error submitting your bad order record.")
    return redirect('bo_list')


@login_required
@user_is_allowed(Feature.TR_BO)
def approve_bo(request, pk):
    this_bo = get_object_or_404(BadOrder, pk=pk)

    if request.method == 'POST':
        this_bo.approve(request.user)
        messages.success(request, "Bad order record is now approved.")

    return redirect('bo_list')


@login_required
@user_is_allowed(Feature.TR_BO)
def reject_bo(request, pk):
    this_bo = get_object_or_404(BadOrder, pk=pk)

    if request.method == 'POST':
        reason = request.POST.get('other_info', None)
        this_bo.reject(request.user, reason)
        messages.success(request, "Bad order record is now rejected.")

    return redirect('bo_list')


@login_required
@user_is_allowed(Feature.TR_BO)
def set_action_taken(request, pk):
    this_bo = get_object_or_404(BadOrder, pk=pk)
    print(request.method)

    if request.method == 'POST':
        action = request.POST.get('other_info', None)
        print(action)
        this_bo.save_action_taken(action, True)
        messages.success(request, "Bad order record is now closed.")

    return redirect('bo_list')