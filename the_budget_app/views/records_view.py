from datetime import datetime

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.db.models import Sum
from django.utils import timezone
from django.db import transaction

from ..models import Ledger, Account, Category
from ..forms import IncomeForm, ExpenseForm, TransferForm


TEMPLATE_RECORD = 'the_budget_app/records/'

INDEX_RECORD = TEMPLATE_RECORD + 'records.html'
DETAIL_RECORD = TEMPLATE_RECORD + 'detail.html'


def index(request):
    all_record = Ledger.objects.all().order_by('-date_created')
    context = {
        'records': all_record
    }

    return render(request, INDEX_RECORD, context)


def detail(request, pk):
    record = Ledger.objects.get(pk=pk)
    context = {
        'record': record,
    }

    return render(request, DETAIL_RECORD, context)


@transaction.atomic
def delete(request, pk):
    """
    Delete the selected budget record.
    """
    if request.method == 'POST':
        record = Ledger.objects.get(pk=pk)
        category_type = record.category.category_type
        account = Account.objects.get(pk=record.account.id)
        if category_type == 'income':
            account.amount -= record.amount
        elif category_type == 'expense':
            account.amount += record.amount
        elif category_type == 'transfer':
            to_account = Account.objects.get(pk=record.to_account.id)
            to_account.amount -= record.amount
            account.amount += record.amount
            to_account.save()
        account.save()
        record.delete()

        messages.success(request, 'Deleted successfully!')
        return redirect(reverse('the_budget:record'))
    return HttpResponseBadRequest('<h1>Request Not Allowed!<h1>')