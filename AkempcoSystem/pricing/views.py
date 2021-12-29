from django.shortcuts import render
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.contrib import messages

from AkempcoSystem.decorators import user_is_allowed
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from fm.models import Product
from fm.views import get_index, add_search_key
from admin_area.models import Feature


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
        object_list = None
        if key:
            object_list = self.model.objects.filter(
                Q(full_description__icontains=key) &
                Q(price_review=True)
            )
        else:
            object_list = self.model.objects.filter(price_review=True)

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