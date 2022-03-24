from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from sales.models import SalesItem, SalesPayment, SalesInvoice


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

    # pass to template
    context = {
        'transaction_count': member.transaction_count,
        'total_amount': total_transaction_amount,
        'payable': total_charges - total_payments,
        'charge_ratio': ratio,
        'transactions': transactions
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