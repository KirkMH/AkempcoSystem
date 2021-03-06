from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q

from django_serverside_datatable.views import ServerSideDatatableView
from AkempcoSystem.decorators import user_is_allowed
from admin_area.models import Feature
from .models import *
from .forms import *

import random
import json

# # function to retrieve the search key
# def get_index(request, index):
#     key = None
#     if index in request.GET:
#         key = request.GET[index]
#     return key


# # function to pass back the search key by adding it to the context
# def add_search_key(request, context):
#     key = get_index(request, "table_search")
#     # pass-back the search key to be displayed in the textbox
#     if key:
#         context["table_search"] = key
#     return context


################################
#   UOM
################################

@login_required()
@user_is_allowed(Feature.FM_UOM)
def uom_list(request):
    return render(request, 'fm/uom_list.html')

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_UOM), name='dispatch')
class UomDTListView(ServerSideDatatableView):
	queryset = UnitOfMeasure.objects.all()
	columns = ['pk', 'uom_description', 'status']

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_UOM), name='dispatch')
class UomCreateView(CreateView):
    model = UnitOfMeasure
    form_class = NewUOMForm
    template_name = 'fm/uom_form.html'

    def post(self, request, *args, **kwargs):
        form = NewUOMForm(request.POST)
        if form.is_valid():
            uom = form.save()
            uom.save()
            messages.success(request, uom.uom_description + " was created successfully.")
            if "another" in request.POST:
                return redirect('new_uom')
            else:
                return redirect('uom_list')
        
        else:
            return render(request, 'fm/uom_new.html', {'form': form})
        

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_UOM), name='dispatch')
class UomUpdateView(SuccessMessageMixin, UpdateView):
    model = UnitOfMeasure
    context_object_name = 'uom'
    form_class = UpdateUOMForm
    template_name = "fm/uom_form.html"
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('uom_list')
    success_message = "%(uom_description)s was updated successfully."



################################
#   Category
################################

@login_required()
@user_is_allowed(Feature.FM_CATEGORY)
def category_list(request):
    return render(request, 'fm/category_list.html')

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_CATEGORY), name='dispatch')
class CategoryDTListView(ServerSideDatatableView):
	queryset = Category.objects.all()
	columns = ['pk', 'category_description', 'status']
    
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_UOM), name='dispatch')
class CategoryCreateView(CreateView):
    model = Category
    form_class = NewCategoryForm
    template_name = 'fm/category_form.html'

    def post(self, request, *args, **kwargs):
        form = NewCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            category.save()
            messages.success(request, category.category_description + " was created successfully.")
            if "another" in request.POST:
                return redirect('new_category')
            else:
                return redirect('category_list')
        
        else:
            return render(request, 'fm/category_new.html', {'form': form})
        

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_UOM), name='dispatch')
class CategoryUpdateView(SuccessMessageMixin, UpdateView):
    model = Category
    context_object_name = 'category'
    form_class = UpdateCategoryForm
    template_name = "fm/category_form.html"
    pk_url_kwarg = 'pk'
    success_message = "%(category_description)s was updated successfully."
    success_url = reverse_lazy('category_list')

    
################################
#   Supplier
################################

@login_required()
@user_is_allowed(Feature.FM_SUPPLIER)
def supplier_list(request):
    return render(request, 'fm/supplier_list.html')

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_SUPPLIER), name='dispatch')
class SupplierDTListView(ServerSideDatatableView):
	queryset = Supplier.objects.all()
	columns = ['pk', 'supplier_name', 'address', 'contact_person', 'contact_info', 'email', 'less_vat', 'status']

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_SUPPLIER), name='dispatch')
class SupplierDetailView(DetailView):
    model = Supplier
    template_name = "fm/supplier_detail.html"
    context_object_name = 'supplier'


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_SUPPLIER), name='dispatch')
class SupplierCreateView(CreateView):
    model = Supplier
    form_class = NewSupplierForm
    template_name = 'fm/supplier_form.html'

    def post(self, request, *args, **kwargs):
        form = NewSupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            supplier.save()
            messages.success(request, supplier.supplier_name + " was created successfully.")
            if "another" in request.POST:
                return redirect('new_supplier')
            else:
                return redirect('supplier_list')
        
        else:
            return render(request, 'fm/supplier_new.html', {'form': form})
        

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_SUPPLIER), name='dispatch')
class SupplierUpdateView(SuccessMessageMixin, UpdateView):
    model = Supplier
    context_object_name = 'supplier'
    form_class = NewSupplierForm
    template_name = "fm/supplier_form.html"
    pk_url_kwarg = 'pk'
    success_message = "%(supplier_name)s was updated successfully."
    success_url = reverse_lazy('supplier_list')


################################
#   Product
################################

@login_required()
@user_is_allowed(Feature.FM_PRODUCT)
def product_list(request):
    return render(request, 'fm/product_list.html')

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_PRODUCT), name='dispatch')
class ProductDTListView(ServerSideDatatableView):
	queryset = Product.objects.all()
	columns = ['pk', 'barcode', 'full_description', 'category__category_description', 'wholesale_qty', 'is_consignment', 'status']  


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_PRODUCT), name='dispatch')
class ProductDetailView(DetailView):
    model = Product
    template_name = "fm/product_detail.html"
    context_object_name = 'product'


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_PRODUCT), name='dispatch')
class ProductCreateView(CreateView):
    def get(self, request, *args, **kwargs):
        suppliers = Supplier.objects.filter(status='ACTIVE')
        context = {
            'form': NewProductForm(),
            'suppliers': suppliers
        }
        return render(request, 'fm/product_form.html', context)

    def post(self, request, *args, **kwargs):
        form = NewProductForm(request.POST)
        suppliers = request.POST.getlist('suppliers')
        if form.is_valid() and len(suppliers) > 0:
            product = form.save()
            for supplier in suppliers:
                sup = Supplier.objects.get(pk=supplier)
                product.suppliers.add(sup)
            messages.success(request, product.full_description + " was created successfully.")
            if "another" in request.POST:
                return redirect('new_product')
            else:
                return redirect('product_list')
        
        else:
            return render(request, 'fm/product_new.html', {'form': form})
        

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_PRODUCT), name='dispatch')
class ProductUpdateView(SuccessMessageMixin, UpdateView):
    model = Product
    form_class = UpdateProductForm
    context_object_name = 'product'
    template_name = "fm/product_form.html"
    pk_url_kwarg = 'pk'
    success_message = "%(full_description)s was updated successfully."

    def get_context_data(self, **kwargs):
        product = Product.objects.get(pk=self.object.pk)
        list=[]
        for supplier in product.suppliers.all():
            list.append(supplier.pk)
        context = super().get_context_data(**kwargs)
        context["suppliers"] = Supplier.objects.filter(status='ACTIVE')
        context["selected_suppliers"] = list

        return context    

    def form_valid(self, form):
        product = form.save()
        suppliers = self.request.POST.getlist('suppliers')
        product.suppliers.clear()
        for supplier in suppliers:
            sup = Supplier.objects.get(pk=supplier)
            product.suppliers.add(sup)

        return redirect('product_detail', pk=product.pk)


def generate_barcode_number(request):
    barcode = random.randint(1000000000000, 9999999999999)
    # make sure that this is unique
    while Product.objects.filter(barcode=barcode).exists():
        barcode = random.randint(1000000000000, 9999999999999)

    return HttpResponse(json.dumps({'barcode': barcode}), content_type="application/json")