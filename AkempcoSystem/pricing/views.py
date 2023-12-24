from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django_serverside_datatable.views import ServerSideDatatableView

from AkempcoSystem.decorators import user_is_allowed
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from fm.models import Product
from admin_area.models import Feature, Store
from stocks.models import WarehouseStock, StoreStock
from .models import ProductPricing
# from fm.views import get_index, add_search_key
from .forms import NewProductPricingForm


# for pagination
MAX_ITEMS_PER_PAGE = 10


@login_required
@user_is_allowed(Feature.TR_PRICING)
def product_pricing_list(request):
    context = {'type': 'selected'}
    return render(request, "pricing/pricing_review.html", context)

# List of Product with prices for approval


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PRICING), name='dispatch')
class ProductPricingDTListView(ServerSideDatatableView):
    queryset = Product.objects.filter(
        Q(for_price_review=True) |
        Q(selling_price=0)
    )
    columns = ['pk', 'full_description', 'latest_supplier_price',
               'selling_price', 'wholesale_price', 'wholesale_qty']


@login_required
@user_is_allowed(Feature.TR_PRICING)
def all_product_pricing_list(request):
    context = {'type': 'all'}
    return render(request, "pricing/pricing_review.html", context)

# List of all products with their prices


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PRICING), name='dispatch')
class AllProductPricingDTListView(ServerSideDatatableView):
    model = Product
    columns = ['pk', 'full_description', 'latest_supplier_price',
               'selling_price', 'wholesale_price', 'wholesale_qty']


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PRICING), name='dispatch')
class ProductPricingCreateView(CreateView):
    model = ProductPricing
    form_class = NewProductPricingForm
    template_name = 'pricing/pricing_form.html'
    success_url = reverse_lazy('price_review')

    def get_initial(self):
        rp = 0
        wp = 0
        try:
            product = Product.objects.get(pk=self.kwargs['pk'])
            rp = product.get_recommended_retail_price()
            wp = product.get_recommended_wholesale_price()
        except Exception as e:
            messages.error(self.request, 'Error: ' + str(e))
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
        messages.success(self.request, 'The selling price of ' +
                         product.full_description + ' is now updated.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product"] = get_object_or_404(Product, pk=self.kwargs['pk'])
        context["store_count"] = Store.objects.count()
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
        context["st"] = StoreStock.availableStocks.filter(
            product=prod).order_by('-pk')
        return context
