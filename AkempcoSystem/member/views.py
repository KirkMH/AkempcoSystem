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
	columns = ['pk', 'name', 'address', 'creditor_type', 'credit_limit', 'active']
    
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
    
@login_required()
def transaction_history(request):
    # for transaction history
    member = request.user.userdetail.linked_creditor_acct
    transactions = member.get_all_transactions()

    # pass to template
    context = {
        'transactions': transactions
    }
    return render(request, 'member/transaction_history.html', context)

    
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


@method_decorator(login_required, name='dispatch')
class PayableListView(ListView):
    context_object_name = 'creditors'
    template_name = "member/payable_list.html"
    model = Creditor
	
    def get_queryset(self):
        return super().get_queryset().filter(active=True)

    
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
            payment.creditor = get_object_or_404(Creditor, pk=kwargs['pk'])
            payment.posted_by = request.user
            payment.save()
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