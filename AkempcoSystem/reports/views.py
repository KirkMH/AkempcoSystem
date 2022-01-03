from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q

from fm.views import get_index, add_search_key

from AkempcoSystem.decorators import user_is_allowed
from admin_area.models import Feature, Store
from fm.models import Product
from stocks.models import ProductHistory


MAX_ITEMS_PER_PAGE = 10

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.RP_PRODHIST), name='dispatch')
class ProductListView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = "reports/product_list_hist.html"
    paginate_by = MAX_ITEMS_PER_PAGE

    def get_queryset(self):
        # check if the user searched for something
        key = get_index(self.request, "table_search")
        object_list = self.model.objects.all()
        if key:
            object_list = object_list.filter(
                Q(barcode__icontains=key) |
                Q(short_name__icontains=key) |
                Q(category__category_description__icontains=key)
            )
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return add_search_key(self.request, context)  


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.RP_PRODHIST), name='dispatch')
class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'reports/product_history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["akempco"] = Store.objects.all().first()
        context["w_history"] = ProductHistory.for_warehouse.filter(product=self.object)[:50]
        context["s_history"] = ProductHistory.for_store.filter(product=self.object)[:50]
        return context
    