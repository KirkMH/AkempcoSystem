from reports.models import InventoryCountItem
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse 
from django.views.generic import DetailView, CreateView, UpdateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import F
from django_serverside_datatable.views import ServerSideDatatableView
import csv
import io

# from fm.views import get_index, add_search_key

from AkempcoSystem.decorators import user_is_allowed
from admin_area.models import Feature, Store
from fm.models import Product
from stocks.models import ProductHistory, StockAdjustment
from sales.models import ZReading, Sales, ProductSalesReportItem
from .models import InventoryCountReport
from .forms import InventoryCountReportForm


@login_required
@user_is_allowed(Feature.RP_PRODHIST)
def product_list_history(request):
    return render(request, "reports/product_list_hist.html")

# @method_decorator(login_required, name='dispatch')
# @method_decorator(user_is_allowed(Feature.RP_PRODHIST), name='dispatch')
# class ProductDetailView(DetailView):
#     model = Product
#     context_object_name = 'product'
#     template_name = 'reports/product_history.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["akempco"] = Store.objects.all().first()
#         context["w_history"] = ProductHistory.for_warehouse.filter(product=self.object)[:50]
#         context["s_history"] = ProductHistory.for_store.filter(product=self.object)[:50]
#         return context


@login_required
@user_is_allowed(Feature.RP_PRODHIST)
def product_warehouse_history(request, pk):
    akempco = Store.objects.all().first()
    context = {
        'akempco': akempco,
        'product': get_object_or_404(Product, pk=pk)
    }
    return render(request, 'reports/product_history_warehouse.html', context)


@method_decorator(login_required, name='dispatch')
class ProductWarehouseDTView(ServerSideDatatableView):

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk', 0)
        product = get_object_or_404(Product, pk=pk)
        self.queryset = ProductHistory.for_warehouse.filter(product=product)
        self.columns = ['pk', 'performed_on', 'quantity', 'remarks',
                        'performed_by__first_name', 'performed_by__last_name', 'balance']
        return super().get(request, *args, **kwargs)


@login_required
@user_is_allowed(Feature.RP_PRODHIST)
def product_store_history(request, pk):
    akempco = Store.objects.all().first()
    context = {
        'akempco': akempco,
        'product': get_object_or_404(Product, pk=pk)
    }
    return render(request, 'reports/product_history_store.html', context)


@method_decorator(login_required, name='dispatch')
class ProductStoreDTView(ServerSideDatatableView):

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk', 0)
        product = get_object_or_404(Product, pk=pk)
        self.queryset = ProductHistory.for_store.filter(product=product)
        self.columns = ['pk', 'performed_on', 'quantity', 'remarks',
                        'performed_by__first_name', 'performed_by__last_name', 'balance']
        return super().get(request, *args, **kwargs)


@login_required
@user_is_allowed(Feature.RP_CRITICAL)
def critical_products(request):
    akempco = Store.objects.all().first()
    context = {
        'akempco': akempco
    }
    return render(request, 'reports/critical_level.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.RP_CRITICAL), name='dispatch')
class CriticalStockDTListView(ServerSideDatatableView):
    queryset = Product.objects.filter(total_stocks__lte=F('reorder_point'))
    columns = ['pk', 'barcode', 'full_description', 'warehouse_stocks', 'store_stocks',
               'total_stocks', 'reorder_point', 'category__category_description', 'ceiling_qty']


@login_required
@user_is_allowed(Feature.RP_ITR)
def inventoryTurnoverRatio(request):
    # update inventory turnover ratios of all products
    products = Product.objects.filter(status='ACTIVE')
    for p in products:
        p.compute_itr()
    # render the page
    akempco = Store.objects.all().first()
    context = {
        'akempco': akempco
    }
    return render(request, 'reports/inventory_turnover_ratio.html', context)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.RP_ITR), name='dispatch')
class InventoryTurnoverRatioDTView(ServerSideDatatableView):

    def get(self, request, *args, **kwargs):
        products = Product.objects.filter(status='ACTIVE')

        self.queryset = products
        self.columns = ['pk', 'barcode', 'full_description',
                        'cogs', 'avg_inventory', 'itr']
        return super().get(request, *args, **kwargs)


@login_required
def daily_sales_report(request):
    akempco = Store.objects.all().first()
    context = {
        'akempco': akempco,
    }
    return render(request, 'reports/sales_report_daily.html', context)


@method_decorator(login_required, name='dispatch')
class GenerateDailySalesReport(ServerSideDatatableView):

    def get(self, request, *args, **kwargs):
        fromDate = request.GET.get('from', 0)
        toDate = request.GET.get('to', 0)
        print(fromDate, toDate)

        if fromDate == 0 or toDate == 0:
            messages.error(request, 'Please select a valid date range')
            return redirect('sales_report_daily')

        elif fromDate > toDate:
            messages.error(request, 'From date should be less than to date')
            return redirect('sales_report_daily')

        qs = ZReading.objects.filter(
            xreading__created_at__date__range=(fromDate, toDate))
        print(qs)

        self.queryset = qs
        self.columns = ['pk', 'xreading__created_at', 'xreading__transaction_count',
                        'xreading__void_count', 'xreading__total_sales']
        return super().get(request, *args, **kwargs)


@login_required
def product_sales_report(request):
    akempco = Store.objects.all().first()
    context = {
        'akempco': akempco,
    }
    return render(request, 'reports/sales_report_product.html', context)


@method_decorator(login_required, name='dispatch')
class GenerateProductSalesReport(ServerSideDatatableView):

    def get(self, request, *args, **kwargs):
        fromDate = request.GET.get('from', 0)
        toDate = request.GET.get('to', 0)
        print(fromDate, toDate)

        if fromDate == 0 or toDate == 0:
            messages.error(request, 'Please select a valid date range')
            return redirect('product_sales_report')

        elif fromDate > toDate:
            messages.error(request, 'From date should be less than to date')
            return redirect('product_sales_report')

        report = Sales.reports.generate_product_sales_report(cashier=request.user, fromDate=fromDate, toDate=toDate)
        print(report)

        self.queryset = ProductSalesReportItem.objects.filter(report=report)
        self.columns = ['pk', 'product__barcode', 'product__full_description', 'number_of_sold_items', 'total_cogs', 'total_sales']
        return super().get(request, *args, **kwargs)



@login_required
def inventory_count(request):
    last_report = InventoryCountReport.objects.last()
    is_last_report_open = False
    if last_report and not last_report.was_completed():
        is_last_report_open = True
    context = {
        'is_last_report_open': is_last_report_open,
    }
    return render(request, "reports/inventory_count.html", context)


@method_decorator(login_required, name='dispatch')
class InventoryCountDTView(ServerSideDatatableView):
    def get(self, request, *args, **kwargs):
        self.queryset = InventoryCountReport.objects.all()
        print(self.queryset)
        self.columns = ['pk', 'description', 'inventory_date', 'warehouse_count_status', 'store_count_status', 'overall_status', 'generated_by__username', 'created_at']
        return super().get(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class InventoryCountCreateView(CreateView):
    model = InventoryCountReport
    template_name = 'reports/inventory_count_new.html'
    form_class = InventoryCountReportForm

    def form_valid(self, form):
        form.instance.generated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('inventory_count_view', kwargs={'pk': self.object.pk})


@method_decorator(login_required, name='dispatch')
class InventoryCountUpdateView(UpdateView):
    model = InventoryCountReport
    template_name = 'reports/inventory_count_new.html'
    form_class = InventoryCountReportForm

    def form_valid(self, form):
        form.instance.generated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('inventory_count_view', kwargs={'pk': self.object.pk})


@method_decorator(login_required, name='dispatch')
class InventoryCountDetailView(DetailView):
    model = InventoryCountReport
    template_name = 'reports/inventory_count_detail.html'
    context_object_name = 'report'


@login_required
def show_inventory_cycle(request, pk):
    report = InventoryCountReport.objects.get(pk=pk)
    location = request.GET.get('location', 'warehouse')
    cycle_count = request.GET.get('cycle', 1)
    is_open = True
    if location == 'warehouse' and report.was_warehouse_count_completed():
        is_open = False
    elif location == 'store' and report.was_store_count_completed():
        is_open = False

    data = report.get_summary(location, cycle_count)

    context = {
        'report': report,
        'location': location,
        'cycle_count': cycle_count,
        'is_open': is_open,
        'data': data
    }
    print(f"context: {context}")
    return render(request, 'reports/inventory_count_cycle.html', context)


@method_decorator(login_required, name='dispatch')
class InventoryCountCycleDTView(ServerSideDatatableView):
    def get(self, request, *args, **kwargs):
        report = InventoryCountReport.objects.get(pk=kwargs['pk'])
        location = request.GET.get('location', 'warehouse')
        cycle_count = request.GET.get('cycle_count', 1)
        print(f"request.GET: {request.GET}, location: {location}, cycle_count: {cycle_count}")
        self.queryset = InventoryCountItem.objects.filter(report=report, location=location, cycle=cycle_count)
        self.columns = ['pk', 'product__barcode', 'product__full_description', 'expected_count', 'physical_count', 'variance']
        return super().get(request, *args, **kwargs)


@login_required
def upload_inventory_count(request, pk, location, cycle):
    report = InventoryCountReport.objects.get(pk=pk)
    print(f'location: {location}, cycle: {cycle}')

    # Read the CSV file with different encodings
    csv_file = request.FILES['file']
    file_content = csv_file.read()
    
    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    data_set = None
    
    for encoding in encodings:
        try:
            data_set = file_content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    
    if data_set is None:
        raise ValueError("Failed to decode the file. Please ensure the file is in a supported encoding (UTF-8, Latin-1, Windows-1252, or ISO-8859-1).")

    io_string = io.StringIO(data_set)
    # Skip header row
    next(io_string, None)
    
    csv_reader = csv.reader(io_string, delimiter=',', quotechar='"')
    rows = list(csv_reader)
    
    # Collect valid product IDs
    product_ids = [int(row[0]) for row in rows if row and row[0].isdigit()]
    
    # Batch fetch products using in_bulk
    products_map = Product.objects.in_bulk(product_ids)
    
    inventory_items = []
    has_no_discrepancy = True
    
    # loop through the rows
    for row in rows:
        # if row[0] is non-numeric, skip it
        if not row or not row[0].isdigit():
            continue
            
        product_id = int(row[0])
        product = products_map.get(product_id)
        
        if not product:
            continue
            
        # get the expected count
        if location.lower() == 'store':
            expected_count = product.store_stocks
        else:
            expected_count = product.warehouse_stocks
            
        # get the physical count
        physical_count = int(row[3] or 0)
        if location.lower() == 'store':
            if cycle > 1 and product.store_count != physical_count:
                has_no_discrepancy = False
            product.store_count = physical_count
        else:
            if cycle > 1 and product.warehouse_count != physical_count:
                has_no_discrepancy = False
            product.warehouse_count = physical_count
        
        # get the variance
        variance = physical_count - expected_count

        # prepare the inventory count item
        inventory_items.append(
            InventoryCountItem(
                report=report,
                location=location,
                cycle=cycle,
                product=product,
                physical_count=physical_count,
                expected_count=expected_count,
                variance=variance
            )
        )
        
    # Bulk create items
    if inventory_items:
        InventoryCountItem.objects.bulk_create(inventory_items)
        report.update_completed_date(location, cycle)

        # save the products
        Product.objects.bulk_update(products_map.values(), ['store_count', 'warehouse_count'])

        if (cycle > 1 and has_no_discrepancy) or cycle == 3:
            # auto-accept
            return redirect(reverse('accept_inventory_count', args=[pk, location, cycle]))
    else:
        messages.warning(request, 'No valid products found in the uploaded file.')
    
    url = reverse('show_inventory_cycle', args=[pk])
    return redirect(url + f'?location={location}&cycle={cycle}')


def accept_inventory_count(request, pk, location, cycle):
    report = InventoryCountReport.objects.get(pk=pk)
    
    products = Product.objects.all()
    if location.lower() == 'store':
        products = products.exclude(store_stocks=F('store_count'))
        report.store_count_status = 'Completed'
    else:
        products = products.exclude(warehouse_stocks=F('warehouse_count'))
        report.warehouse_count_status = 'Completed'

    for product in products:
        adjustment = StockAdjustment()
        adjustment.product = product
        adjustment.location = 0 if location.lower() == 'warehouse' else 1
        adjustment.quantity = product.store_count - product.store_stocks if location.lower() == 'store' else product.warehouse_count - product.warehouse_stocks
        adjustment.reason = 'Inventory count adjustment'
        adjustment.created_by = request.user
        adjustment.save()
        adjustment.perform(request.user)

    report.save()
    url = reverse('show_inventory_cycle', args=[pk])
    return redirect(url + f'?location={location}&cycle={cycle}')