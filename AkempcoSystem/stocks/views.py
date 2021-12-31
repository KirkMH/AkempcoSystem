from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import Q

from AkempcoSystem.decorators import user_is_allowed
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from fm.models import Product
from admin_area.models import Feature
from fm.views import get_index, add_search_key
from .models import RequisitionVoucher


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_STOCKS), name='dispatch')
class StockListView(ListView):
    model = Product
    context_object_name = "product"
    template_name = "stocks/stock_list.html"

    def get_queryset(self):
        # check if the user searched for something
        key = get_index(self.request, "table_search")
        object_list = self.model.objects.all()
        if key:
            object_list = object_list.filter(
                Q(full_description__icontains=key)
            )
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return add_search_key(self.request, context)


class RVListView(ListView):
    model = RequisitionVoucher
    context_object_name = "rv"
    template_name = "stocks/requisition_voucher.html"

    def get_queryset(self):
        # check if the user searched for something
        key = get_index(self.request, "table_search")
        object_list = self.model.objects.all()
        if key:
            object_list = object_list.filter(
                Q(pk=key)
            )
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return add_search_key(self.request, context)