from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q

from AkempcoSystem.decorators import user_is_allowed
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from fm.models import Product
from admin_area.models import Feature
from stocks.models import WarehouseStock, StoreStock
from .models import ProductPricing
from fm.views import get_index, add_search_key
from .forms import NewProductPricingForm


# for pagination
MAX_ITEMS_PER_PAGE = 10


# List of Product with prices for approval
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PRICING), name='dispatch')
class ProductPricingListView(ListView):
    model = Product
    context_object_name = 'products'
    paginate_by = MAX_ITEMS_PER_PAGE
    template_name = "pricing/pricing_review.html"

    def get_queryset(self):
        # check if the user searched for something
        key = get_index(self.request, "table_search")
        object_list = self.model.objects.filter(
            Q(for_price_review=True) |
            Q(selling_price=0)
        )
        if key:
            object_list = object_list.filter(full_description__icontains=key)

        return object_list


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = "selected"
        return context


# List of all products with their prices
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PRICING), name='dispatch')
class AllProductPricingListView(ListView):
    model = Product
    context_object_name = 'products'
    paginate_by = MAX_ITEMS_PER_PAGE
    template_name = "pricing/pricing_review.html"

    def get_queryset(self):
        # check if the user searched for something
        key = get_index(self.request, "table_search")
        object_list = None
        if key:
            object_list = self.model.objects.filter(
                Q(full_description__icontains=key)
            )
        else:
            object_list = self.model.objects.all()

        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type"] = "all"
        return context

        
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PRICING), name='dispatch')
class ProductPricingCreateView(CreateView):
    model = ProductPricing
    form_class = NewProductPricingForm
    template_name = 'pricing/pricing_form.html'
    success_url = reverse_lazy('price_review')

    def get_initial(self):
        product = Product.objects.get(pk=self.kwargs['pk'])
        rp = product.get_recommended_retail_price()
        wp = product.get_recommended_wholesale_price()
        return {
            'retail_price': rp,
            'wholesale_price': wp
        }

    def form_valid(self, form):
        product = Product.objects.get(pk=self.kwargs['pk'])
        product.selling_price = form.cleaned_data['retail_price']
        product.wholesale_price = form.cleaned_data['wholesale_price']
        product.for_price_review = False
        product.save()
        form.instance.product = product
        form.instance.price_tagged_by = self.request.user
        messages.success(self.request, 'The selling price of ' + product.full_description + ' is now updated.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product"] = get_object_or_404(Product, pk=self.kwargs['pk'])
        return context
    
class PricingDetailListView(ListView):
    model = WarehouseStock
    template_name = "pricing/pricing_detail.html"
    context_object_name = "ws"

    def get_queryset(self):
        prod = get_object_or_404(Product, pk=self.kwargs['pk'])
        return WarehouseStock.availableStocks.filter(product=prod).order_by('-date_received')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prod = get_object_or_404(Product, pk=self.kwargs['pk'])
        context["st"] = StoreStock.availableStocks.filter(product=prod).order_by('-pk')
        return context
    