from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import Q
from django.core.paginator import Paginator

from AkempcoSystem.decorators import user_is_allowed
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from admin_area.models import Feature
from fm.views import get_index, add_search_key
from fm.models import Supplier
from .models import PurchaseOrder


# for pagination
MAX_ITEMS_PER_PAGE = 10


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.TR_PURCHASES), name='dispatch')
class PurchaseSupplierListView(ListView):
    model = Supplier
    context_object_name = 'suppliers'
    template_name = "purchases/purchase_supplier.html"
    paginate_by = MAX_ITEMS_PER_PAGE

    def get_queryset(self):
        # check if the user searched for something
        key = get_index(self.request, "table_search")
        object_list = self.model.objects.all()
        if key:
            object_list = object_list.filter(
                Q(supplier_name__icontains=key)
            )
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cash_purchase = {
            'last_po_date': PurchaseOrder.cash_purchase.get_last_po_date(),
            'last_po_num': PurchaseOrder.cash_purchase.get_last_po_number(),
            'number_of_open_po': PurchaseOrder.cash_purchase.get_number_of_open_po(),
            'completion_rate': PurchaseOrder.cash_purchase.get_completion_rate()
        }
        context['cash_purchase'] = cash_purchase
        return add_search_key(self.request, context)  