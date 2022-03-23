from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required()
def dashboard_member_view(request):
    member = request.user.userdetail.linked_creditor_acct
    if not member:
        return redirect('login')

    total_transaction_amount = member.total_transaction_amount
    total_charges = member.total_charges
    total_payments = member.total_payments
    ratio = (total_charges / total_transaction_amount) * 100

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