from django.shortcuts import render
from django.views.generic import ListView

from AkempcoSystem.decorators import user_is_allowed
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from fm.models import Product
from admin_area.models import Feature


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_STOCKS), name='dispatch')
class StockListView(ListView):
    model = Product
    context_object_name = "product"
    template_name = "stocks/stock_list.html"
