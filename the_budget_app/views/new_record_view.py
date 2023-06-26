from datetime import datetime
from decimal import Decimal as dc

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone

from ..forms import ExpenseForm, IncomeForm, TransferForm
from ..models import Account, Category, Ledger


TEMPLATE_RECORD = 'the_budget_app/new_record/'

RECORD_INDEX = TEMPLATE_RECORD + 'index.html'

INCOME, EXPENSE, TRANSFER = 'income', 'expense', 'transfer'


def income(request):
    """
    Returns a form for new income record.
    """
    if request.method == 'GET':
        split_sum = Account.get_sum_of_splitting_percent()
        form = IncomeForm()
        context = {
            'income_form': form,
        }
        if split_sum != 100:
            context.update({'auto_split_disabled': True})
        return render(request, RECORD_INDEX, context)

    if request.method == 'POST':
        form = IncomeForm(request.POST)
        context = {
            'income_form': form,
        }

        if form.is_valid():
            amount = float(form.cleaned_data['amount'])
            note = form.cleaned_data['note']
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']
            date_modified = datetime.combine(date, time)
            date_modified = timezone.make_aware(date_modified)
            account = form.cleaned_data['account']
            category = form.cleaned_data['category']

            account = Account.objects.get(pk=account)
            category = Category.objects.get(pk=category)

            if form['auto_split'].value() == True:
                # If `auto_split` is enabled, the income fund will
                # be distributed based on the splitting_percent of
                # the accounts.
                accounts = Account.objects.exclude(
                    splitting_percent=0
                )
                remaining_amount = amount
                for account in accounts:
                    if account == accounts.last():
                        # The remaining amount will be added on the
                        # last account.
                        remaining_amount = round(remaining_amount,2)
                        account.amount += remaining_amount
                        account.save()
                        Ledger.objects.create(
                            account=account,
                            category=category,
                            amount=remaining_amount,
                            note=note,
                            date_created=date_modified
                        )
                    else:
                        split_percent = account.splitting_percent * 0.01
                        percent_amount = amount * split_percent
                        percent_amount = round(percent_amount, 2)
                        account.amount += percent_amount
                        remaining_amount -= percent_amount
                        account.save()
                        Ledger.objects.create(
                            account=account,
                            category=category,
                            amount=percent_amount,
                            note=note,
                            date_created=date_modified
                        )
            else:
                new_record = Ledger(
                    account=account,
                    category=category,
                    amount=amount,
                    note=note,
                    date_created=date_modified
                )
                account.amount += amount
                account.save()
                new_record.save()
            context.update({'success': "Income Added Successfully!"})
            messages.success(request, context['success'])
        else:
            context.update({'error': "ValidationError"})
            return render(request, RECORD_INDEX, context)


        return redirect(reverse('the_budget:record'))


def expense(request):
    """
    Returns template for income record.
    """
    if request.method == 'GET':
        form = ExpenseForm()
        context = {
            'expense_form': form,
        }
        return render(request, RECORD_INDEX, context)

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        context = {
            'expense_form': form,
        }

        if form.is_valid():
            amount = float(form.cleaned_data['amount'])
            note = form.cleaned_data['note']
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']
            date_modified = datetime.combine(date, time)
            date_modified = timezone.make_aware(date_modified)
            account = form.cleaned_data['account']
            category = form.cleaned_data['category']

            account = Account.objects.get(pk=account)
            category = Category.objects.get(pk=category)
            new_record = Ledger(
                account=account,
                category=category,
                amount=amount,
                note=note,
                date_created=date_modified
            )
            account.amount -= amount
            account.save()
            new_record.save()
            context.update({'success': "Expense Added Successfully!"})
            messages.success(request, context['success'])
        else:
            context.update({'error': "ValidationError"})
            return render(request, RECORD_INDEX, context)

        return redirect(reverse('the_budget:record'))


def transfer(request):
    """
    Returns template for transfer record.
    """
    if request.method == 'GET':
        form = TransferForm()
        context = {
            'transfer_form': form,
        }
        return render(request, RECORD_INDEX, context)

    if request.method == 'POST':
        form = TransferForm(request.POST)
        context = {
            'transfer_form': form,
        }

        if form.is_valid():
            amount = float(form.cleaned_data['amount'])
            note = form.cleaned_data['note']
            date = form.cleaned_data['date']
            time = form.cleaned_data['time']
            date_modified = datetime.combine(date, time)
            date_modified = timezone.make_aware(date_modified)
            from_account = form.cleaned_data['account']
            to_account = form.cleaned_data['to_account']

            from_account = Account.objects.get(pk=from_account)
            to_account = Account.objects.get(pk=to_account)

            new_record = Ledger(
                    account=from_account,
                    category=Category.get_transfer(),
                    to_account=to_account,
                    amount=amount,
                    note=note,
                    date_created=date_modified
                )
            from_account.amount -= amount
            to_account.amount += amount

            from_account.save()
            to_account.save()
            new_record.save()
            context.update({'success': "Fund Transferred Successfully!"})
            messages.success(request, context['success'])
        else:
            context.update({'error': "ValidationError"})
            return render(request, RECORD_INDEX, context)

        return redirect(reverse('the_budget:record'))
