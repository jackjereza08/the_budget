from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db import transaction

from ..forms import AccountForm
from ..models import Account

# Constant configurations for view.
TEMPLATE_ACCOUNT = 'the_budget_app/accounts/'
# Template Accounts
ACCOUNT_INDEX = TEMPLATE_ACCOUNT + 'index.html'
ACCOUNT_CREATE  = TEMPLATE_ACCOUNT + 'create.html'
ACCOUNT_EDIT  = TEMPLATE_ACCOUNT + 'edit.html'


def index(response):
    """
    Displays list of Accounts of the user.
    """
    accounts = Account.objects.all()
    context = {
        'hello': 'The Budget App',
        'accounts': accounts,
    }
    
    return render(response, ACCOUNT_INDEX, context)


def create(request):
    """
    Create new `Account`. Displays form for creating new `Account`
    and save them if the data meets the validation.
    """
    # Get sum of splitting percent to check the remaining percent
    # for auto split of fund.
    split_remain = 100 - Account.get_sum_of_splitting_percent()

    if request.method == 'GET':
        form = AccountForm(max_value=split_remain)

        context = {
            'form': form,
        }
        if Account.get_sum_of_splitting_percent() == 100:
            context.update({'is_split_disabled': True})    

        return render(request, ACCOUNT_CREATE, context)

    if request.method == 'POST':
        form = AccountForm(split_remain, request.POST)
        context={'form': form}
        if form.is_valid():
            account_name = form.cleaned_data['account_name']
            splitting_percent = form.cleaned_data['splitting_percent']
            initial_amount = form.cleaned_data['initial_amount']

            if splitting_percent == None:
                splitting_percent = 0

            Account.objects.create(
                account_name=account_name,
                splitting_percent=splitting_percent,
                amount=initial_amount,
            )
            messages.success(request, 'Account Added Successfully!')
            return redirect(reverse('the_budget:account'))
        else:
            context.update({'error':'ValidationError'})
            return render(request, ACCOUNT_CREATE, context)


def edit(request, pk):
    """
    Edit selected `Account`.
    """
    account = get_object_or_404(Account,pk=pk)
    split_sum = Account.get_sum_of_splitting_percent()
    split_remain = 100 - split_sum + account.splitting_percent

    # If this account is not the only one exists in the database,
    # will collect all the accounts except the selected account.
    accounts = Account.objects.exclude(pk=pk)

    # This variable is use to remove the splitting percent field on
    # the template.
    disable_split_field = False
    if request.method == 'GET':
        form = AccountForm(initial={
                'account_name': account.account_name,
                'splitting_percent': account.splitting_percent,
                'initial_amount': account.amount,
            },
        max_value=split_remain,
        )

        if split_sum >= 100 and account.splitting_percent == 0:
            disable_split_field = True
        
        context = {
            'form': form,
            'account_id': account.pk,
            'is_split_disabled': disable_split_field,
            'accounts': accounts,
        }

        return render(request, ACCOUNT_EDIT, context)

    if request.method == 'POST':
        form = AccountForm(split_remain, request.POST)
        
        if form.is_valid():
            if form.has_changed():
                account_name = form.cleaned_data['account_name']
                splitting_percent = form.cleaned_data['splitting_percent']
                initial_amount = form.cleaned_data['initial_amount']

                if splitting_percent == None:
                    splitting_percent = 0
                    
                if splitting_percent > split_remain:
                    if split_sum >=100 and account.splitting_percent == 0:
                        disable_split_field = True
                    context = {
                        'form': form,
                        'account_id': account.pk,
                        'is_split_disabled': disable_split_field,
                    }
                    return render(request, ACCOUNT_EDIT, context)
                else:
                    account = Account.objects.get(pk=pk)
                    account.account_name = account_name
                    account.splitting_percent = splitting_percent
                    account.amount = initial_amount
                    account.save()
            else:
                # If nothing changed in the form data, it will just send
                # a success message and redirects to `/accounts`.
                pass
            messages.success(request, 'Account Updated Successfully!')
        else:
            if split_sum >=100 and account.splitting_percent == 0:
                disable_split_field = True
            context = {
                'form': form,
                'account_id': account.pk,
                'is_split_disabled': disable_split_field,
            }
            return render(request, ACCOUNT_EDIT, context)
        
        return redirect(reverse('the_budget:account'))


@transaction.atomic
def delete(request, pk):
    """
    Delete selected `Account`. If an account contains amount, it will
    prompt the user to whether transfer the amount or removes it for
    good.
    """
    if request.method == 'POST':
        account = get_object_or_404(Account,pk=pk)
        accounts_count = Account.objects.count()

        if accounts_count == 1 or account.amount == 0:
            account.delete()
        elif accounts_count > 1 and account.amount != 0:
            if 'transfer' in request.POST:
                # If transfer is True then transfer to a certain account
                # then delete the account.
                transfer_to_account = get_object_or_404(
                    Account,
                    pk=request.POST['transfer_to_account']
                )
                transfer_to_account.amount += account.amount
                transfer_to_account.save()
                account.delete()
            else:
                # Else delete the account completely.
                account.delete()
        else:
            account.delete()
    messages.success(request, 'Deleted Successfully!')
    return redirect(reverse('the_budget:account'))