from django.forms.forms import BaseForm
from django.forms.models import BaseModelForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q

from admin_area.views import is_ajax
from django_serverside_datatable.views import ServerSideDatatableView
from AkempcoSystem.decorators import user_is_allowed
from admin_area.models import Feature, Store
from .models import *
from .forms import *


@login_required()
@user_is_allowed(Feature.TR_BO)
def bo_list(request):
    return render(request, "badorder/bo_list.html")


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_BO), name='dispatch')
class BODTListView(ServerSideDatatableView):
    queryset = BadOrder.objects.all()
    columns = ['pk', 'in_warehouse', 'supplier__supplier_name',
               'date_discovered', 'number_of_items', 'grand_total',
               'action_taken', 'process_step']


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
            messages.success(
                request, "The bad order record was created successfully.")
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
        return reverse('bo_products', kwargs={'pk': self.object.pk})


@login_required
@user_is_allowed(Feature.TR_BO)
def delete_bo(request, pk):
    try:
        rv = get_object_or_404(BadOrder, pk=pk)
        rv.delete()
        messages.success(request, "Bad order record is now deleted.")
        return redirect('bo_list')
    except:
        messages.error(
            request, "There was an error deleting the bad order record. Please try again.")
        return redirect('bo_products', pk=pk)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_BO), name='dispatch')
class BODetailView(DetailView):
    model = BadOrder
    context_object_name = 'badorder'
    template_name = "badorder/bo_products.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = BadOrderItem.objects.filter(
            bad_order=self.object)
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
        context["form"].fields["product"].queryset = Product.objects.filter(
            suppliers=bo.supplier, status='ACTIVE')
        return context

    def form_valid(self, form):
        if not is_ajax(self.request):
            bo = get_object_or_404(BadOrder, pk=self.kwargs['pk'])
            new_qty = form.instance.quantity
            old_qty = bo.get_product_qty(form.instance.product)
            form.instance.quantity = new_qty + old_qty
            form.instance.bad_order = bo
            form.instance.requested_by = self.request.user
            boi: BadOrderItem = form.save()
            boi.fill_in_other_fields()
            bo.fill_in_other_fields()

        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('bo_products', kwargs={'pk': self.kwargs['pk']})


@login_required
@user_is_allowed(Feature.TR_BO)
def delete_bo_product(request, pk):
    bo_pk = 0
    try:
        boi = get_object_or_404(BadOrderItem, pk=pk)
        bo = boi.bad_order
        bo_pk = bo.pk
        prod = boi.product.full_description
        boi.delete()
        bo.fill_in_other_fields()
        messages.success(
            request, prod + " was removed from the bad order record.")
    except Exception as e:
        print(f'Error: {e}')
        messages.error(
            request, "There was an error removing the product from the bad order record.")
    return redirect('bo_products', pk=bo_pk)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_BO), name='dispatch')
class BOProductUpdateView(BSModalUpdateView):
    template_name = 'badorder/bo_product_add.html'
    model = BadOrderItem
    form_class = BadOrderItemForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"].fields["product"].queryset = Product.objects.filter(
            status='ACTIVE')
        return context

    def get_success_url(self):
        self.object.fill_in_other_fields()
        bo = self.object.bad_order
        bo.fill_in_other_fields()
        bo_pk = bo.pk
        return reverse('bo_products',
                       kwargs={'pk': bo_pk})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_BO), name='dispatch')
class PrintBODetailView(DetailView):
    model = BadOrder
    context_object_name = 'badorder'
    template_name = "badorder/bo_print.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = BadOrderItem.objects.filter(
            bad_order=self.object)
        context["akempco"] = Store.objects.all().first()
        return context


@login_required
@user_is_allowed(Feature.TR_BO)
def submit_bo(request, pk):
    bo = get_object_or_404(BadOrder, pk=pk)
    if request.method == 'POST':
        result = bo.submit(request.user)
        if result == True:
            messages.success(
                request, "Bad order record was submitted for approval.")
        else:
            messages.error(
                request, f"Error: {result}")
    return redirect('bo_list')


@login_required
@user_is_allowed(Feature.TR_BO)
def approve_bo(request, pk):
    this_bo = get_object_or_404(BadOrder, pk=pk)

    if request.method == 'POST':
        this_bo.approve(request.user)
        messages.success(request, "Bad order record is now approved.")

    return redirect('bo_products',
                    pk=pk)


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
