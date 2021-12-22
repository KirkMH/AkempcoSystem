from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q

from AkempcoSystem.decorators import user_is_allowed
from admin_area.models import Feature
from .models import *
from .forms import *


# used by pagination
MAX_ITEMS_PER_PAGE = 10

# function to retrieve the search key
def get_index(request, index):
    key = None
    if index in request.GET:
        key = request.GET[index]
    return key


# function to pass back the search key by adding it to the context
def add_search_key(request, context):
    key = get_index(request, "table_search")
    # pass-back the search key to be displayed in the textbox
    if key:
        context["table_search"] = key
    return context


################################
#   UOM
################################

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_UOM), name='dispatch')
class UomListView(ListView):
    model = UnitOfMeasure
    context_object_name = 'uoms'
    template_name = "fm/uom_list.html"
    paginate_by = MAX_ITEMS_PER_PAGE

    def get_queryset(self):
        # check if the user searched for something
        key = get_index(self.request, "table_search")
        object_list = self.model.objects.all()
        if key:
            object_list = object_list.filter(
                Q(uom_description__icontains=key) |
                Q(status__icontains=key)
            )
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return add_search_key(self.request, context)    
    
    
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
            if "another" in request.POST:
                return redirect('new_uom')
            else:
                return redirect('uom_list')
        
        else:
            return render(request, 'fm/uom_new.html', {'form': form})
        

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_UOM), name='dispatch')
class UomUpdateView(UpdateView):
    model = UnitOfMeasure
    context_object_name = 'uom'
    form_class = UpdateUOMForm
    template_name = "fm/uom_form.html"
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('uom_list')



################################
#   Category
################################

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_CATEGORY), name='dispatch')
class CategoryListView(ListView):
    model = Category
    context_object_name = 'categories'
    template_name = "fm/category_list.html"
    paginate_by = MAX_ITEMS_PER_PAGE

    def get_queryset(self):
        # check if the user searched for something
        key = get_index(self.request, "table_search")
        object_list = self.model.objects.all()
        if key:
            object_list = object_list.filter(
                Q(category_description__icontains=key) |
                Q(status__icontains=key)
            )
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return add_search_key(self.request, context)    
    
    
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_UOM), name='dispatch')
class CategoryCreateView(CreateView):
    model = Category
    form_class = NewCategoryForm
    template_name = 'fm/category_form.html'

    def post(self, request, *args, **kwargs):
        form = NewCategoryForm(request.POST)
        if form.is_valid():
            uom = form.save()
            uom.save()
            if "another" in request.POST:
                return redirect('new_category')
            else:
                return redirect('category_list')
        
        else:
            return render(request, 'fm/category_new.html', {'form': form})
        

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_UOM), name='dispatch')
class CategoryUpdateView(UpdateView):
    model = Category
    context_object_name = 'category'
    form_class = UpdateCategoryForm
    template_name = "fm/category_form.html"
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('category_list')

    
################################
#   Supplier
################################

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_SUPPLIER), name='dispatch')
class SupplierListView(ListView):
    model = Supplier
    context_object_name = 'suppliers'
    template_name = "fm/supplier_list.html"
    paginate_by = MAX_ITEMS_PER_PAGE

    def get_queryset(self):
        # check if the user searched for something
        key = get_index(self.request, "table_search")
        object_list = self.model.objects.all()
        if key:
            object_list = object_list.filter(
                Q(supplier_name__icontains=key) |
                Q(address__icontains=key) |
                Q(contact_person__icontains=key) |
                Q(contact_number__icontains=key) |
                Q(email__icontains=key) |
                Q(status__icontains=key)
            )
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return add_search_key(self.request, context)       


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
            uom = form.save()
            uom.save()
            if "another" in request.POST:
                return redirect('new_supplier')
            else:
                return redirect('supplier_list')
        
        else:
            return render(request, 'fm/supplier_new.html', {'form': form})
        

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_SUPPLIER), name='dispatch')
class SupplierUpdateView(UpdateView):
    model = Supplier
    context_object_name = 'supplier'
    form_class = NewSupplierForm
    template_name = "fm/supplier_form.html"
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('supplier_list')