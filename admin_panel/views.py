from functools import wraps

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.transaction import atomic
from django.shortcuts import render, redirect

from admin_panel.forms import BtcApproveAdminForm, EthApproveAdminForm, MakeTopUpForm
from core.models import Transaction
from core.models.inouts.transaction import REASON_MANUAL_TOPUP
from core.utils.wallet_history import create_or_update_wallet_history_item_from_transaction
from cryptocoins.coins.btc.service import BTCCoinService
from cryptocoins.coins.eth import ETH_CURRENCY
from cryptocoins.coins.usdt import USDT_CURRENCY
from cryptocoins.tasks import process_payouts
from cryptocoins.utils.commons import get_withdrawal_requests_to_process


@staff_member_required
def make_topup(request):
    if request.method == 'POST':
        form = MakeTopUpForm(request.POST)

        try:
            if form.is_valid():
                currency = form.cleaned_data.get('currency')
                amount = form.cleaned_data.get('amount')
                user = form.cleaned_data.get('user')
                with atomic():
                    tx = Transaction.topup(user.id, currency, amount, {'1': 1}, reason=REASON_MANUAL_TOPUP)
                    create_or_update_wallet_history_item_from_transaction(tx)
                messages.success(request, 'Top-Up completed')
                return redirect('admin_make_topup')  # need for clear post data
        except Exception as e:  # all messages and errors to admin message
            messages.error(request, e)
    else:
        form = MakeTopUpForm()

    return render(request, 'admin/form.html', context={
        'form': form,
    })


@staff_member_required
def admin_withdrawal_request_approve(request):
    service = BTCCoinService()
    withdrawal_requests = service.get_withdrawal_requests()

    if request.method == 'POST':
        form = BtcApproveAdminForm(request.POST)

        try:
            if form.is_valid():
                private_key = form.cleaned_data.get('key')
                service.process_withdrawals(private_key=private_key)
                messages.success(request, 'Withdrawal completed')
                return redirect('admin_withdrawal_request_approve_btc')  # need for clear post data
        except Exception as e:  # all messages and errors to admin message
            messages.error(request, e)
    else:
        form = BtcApproveAdminForm()

    return render(request, 'admin/withdrawal/request_approve_form.html', context={
        'form': form,
        'withdrawal_requests': withdrawal_requests,
        'withdrawal_requests_column': [
            {'label': 'user', 'param': 'user'},
            {'label': 'confirmed', 'param': 'confirmed'},
            {'label': 'currency', 'param': 'currency'},
            {'label': 'state', 'param': 'state'},
            {'label': 'details', 'param': 'data.destination'},
        ]
    })


@staff_member_required
def admin_eth_withdrawal_request_approve(request):
    withdrawal_requests = get_withdrawal_requests_to_process([ETH_CURRENCY, USDT_CURRENCY], blockchain_currency='ETH')

    if request.method == 'POST':
        form = EthApproveAdminForm(request.POST)

        try:
            if form.is_valid():
                password = form.cleaned_data.get('key')
                process_payouts.apply_async([password,])
                messages.success(request, 'Withdrawals in processing')
                return redirect('admin_withdrawal_request_approve_eth')  # need for clear post data
        except Exception as e:  # all messages and errors to admin message
            messages.error(request, e)
    else:
        form = EthApproveAdminForm()

    return render(request, 'admin/withdrawal/request_approve_form.html', context={
        'form': form,
        'withdrawal_requests': withdrawal_requests,
        'withdrawal_requests_column': [
            {'label': 'user', 'param': 'user'},
            {'label': 'confirmed', 'param': 'confirmed'},
            {'label': 'currency', 'param': 'currency'},
            {'label': 'state', 'param': 'state'},
            {'label': 'details', 'param': 'data.destination'},
        ]
    })
