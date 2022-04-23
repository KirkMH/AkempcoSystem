import csv, io
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django_serverside_datatable.views import ServerSideDatatableView
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from bootstrap_modal_forms.generic import BSModalCreateView, BSModalUpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from AkempcoSystem.decorators import user_is_allowed

from admin_area.views import is_ajax
from sales.models import SalesItem, SalesPayment, SalesInvoice
from admin_area.models import Feature
from .models import Creditor
from .forms import *

################################
#   Creditor FM
################################

@login_required()
@user_is_allowed(Feature.FM_CREDITOR)
def creditor_list(request):
    return render(request, 'member/creditor_list.html')

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_CREDITOR), name='dispatch')
class CreditorDTListView(ServerSideDatatableView):
	queryset = Creditor.objects.all()
	columns = ['pk', 'name', 'address', 'creditor_type', 'credit_limit', 'active', 'payable']
    
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_CREDITOR), name='dispatch')
class CreditorCreateView(CreateView):
    model = Creditor
    form_class = NewCreditorForm
    template_name = 'member/creditor_form.html'

    def post(self, request, *args, **kwargs):
        form = NewCreditorForm(request.POST)
        if form.is_valid():
            cred = form.save()
            cred.save()
            messages.success(request, cred.name + " was created successfully.")
            if "another" in request.POST:
                return redirect('new_cred')
            else:
                return redirect('cred_list')
        
        else:
            return render(request, 'member/creditor_form.html', {'form': form})
        

@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_allowed(Feature.FM_CREDITOR), name='dispatch')
class CreditorUpdateView(SuccessMessageMixin, UpdateView):
    model = Creditor
    context_object_name = 'creditor'
    form_class = UpdateCreditorForm
    template_name = "member/creditor_form.html"
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('cred_list')
    success_message = "%(name)s was updated successfully."

    def form_valid(self, form):
        cred = form.save()
        cred.fill_in_other_fields()
        return super().form_valid(form)


@login_required()
def dashboard_member_view(request):
    member = request.user.userdetail.linked_creditor_acct
    if not member:
        return redirect('login')

    total_transaction_amount = member.total_transaction_amount
    total_charges = member.total_charges
    total_payments = member.total_payments
    ratio = 0 if total_transaction_amount == 0 else (total_charges / total_transaction_amount) * 100

    # for transaction history
    transactions = member.get_latest_10_transactions()
    payments = member.get_latest_10_payments()

    # pass to template
    context = {
        'transaction_count': member.transaction_count,
        'total_amount': total_transaction_amount,
        'payable': total_charges - total_payments,
        'charge_ratio': ratio,
        'transactions': transactions,
        'payments': payments
    }
    return render(request, 'member/dashboard.html', context)
    
@method_decorator(login_required, name='dispatch')
class TransactionHistoryDTListView(ServerSideDatatableView):
	
    def get(self, request, *args, **kwargs):
        member = request.user.userdetail.linked_creditor_acct
        self.queryset = member.get_all_transactions()
        self.columns = ['pk', 'sales_datetime', 'sales__item_count', 'payment_modes', 'sales__total']
        return super().get(request, *args, **kwargs)
    

def transaction_history(request):
    return render(request, 'member/transaction_history.html')

    
def open_transaction(request, pk):
    si = get_object_or_404(SalesInvoice, pk=pk)
    items = SalesItem.objects.filter(sales=si.sales)
    payments = SalesPayment.objects.filter(sales=si.sales)
    context = {
        'transaction': si,
        'items': items,
        'payments': payments
    }
    return render(request, 'member/sales_invoice.html', context)


#########################################
### Member Payable/Payment Transactions
#########################################

@login_required()
def payable_listview(request):
    return render(request, "member/payable_list.html")
    
class PaymentCreateView(CreateView):
    model = CreditorPayment
    form_class = NewPaymentForm
    template_name = 'member/payment_form.html'
    success_url = reverse_lazy('payable_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["creditor"] = get_object_or_404(Creditor, pk=self.kwargs['pk'])
        return context


    def post(self, request, *args, **kwargs):
        form = NewPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            creditor = get_object_or_404(Creditor, pk=kwargs['pk'])
            payment.creditor = creditor
            payment.posted_by = request.user
            payment.save()
            creditor.fill_in_other_fields()
            messages.success(request, payment.creditor.name + "'s payment was posted successfully.")        
            return redirect('payable_list')
        else:
            return render(request, 'member/payment_form.html', {'form': form})

    
@login_required()
def payment_history(request):
    # for transaction history
    member = request.user.userdetail.linked_creditor_acct
    payments = member.get_all_payments()

    # pass to template
    context = {
        'payments': payments
    }
    return render(request, 'member/payment_history.html', context)


#################################
### CSV File Manipulation
#################################

def download_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="payment.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(["ID (Don't change')", 'Name', 'Payable Amount', 'Amount Paid'])
    creditors = Creditor.objects.filter(active=True)
    for cred in creditors:
        writer.writerow([cred.pk, cred.name, cred.payable])

    return response


def upload_csv(request):
    if request.method == 'GET':
        form = UploadForm()

    # If not GET method then proceed
    else:
        try:
            form = UploadForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data['payment_file']

                if not csv_file.name.endswith('.csv'):
                    print('File is not a CSV type.')
                    messages.error(request, 'File is not a CSV type.')
                
                # If file is too large
                elif csv_file.multiple_chunks():
                    print('Uploaded file is too big (%.2f MB)' %(csv_file.size(1000*1000),))
                    messages.error(request, 'Uploaded file is too big (%.2f MB)' %(csv_file.size(1000*1000),))
                
                else:
                    # save file contents
                    csv_file = request.FILES['payment_file']
                    data_set = csv_file.read().decode('ISO-8859-1')
                    io_string = io.StringIO(data_set)
                    next(io_string)
                    payments = []
                    for col in csv.reader(io_string, delimiter=','):
                        pk = col[0]
                        creditor = Creditor.objects.get(pk=pk)
                        if len(col) == 4:
                            amt = col[3]
                            
                            payment = CreditorPayment(
                                creditor=creditor,
                                amount=amt,
                                posted_by=request.user
                            )
                            payments.append(payment)
                            
                    # actual saving to database
                    for payment in payments:
                        payment.save()

                messages.success(request, "Successully uploaded the file for member payments.")
                return redirect('payable_list')

        except Creditor.DoesNotExist:
            messages.error(request, 'Unable to save payments because at least one ID has been changed. Please re-upload with correct member IDs.')
            return redirect('payable_list')

        except Exception as e:
            messages.error(request, 'Unable to upload file. ' + repr(e))

    return render(request, 'member/upload_form.html', {'form': form})