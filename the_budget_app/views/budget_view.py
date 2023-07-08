from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from ..models import Budget, Category, Ledger
from ..forms import BudgetForm


# Constant configurations for view.
TEMPLATE_BUDGET = 'the_budget_app/budget/'
# Template Accounts
BUDGET_INDEX = TEMPLATE_BUDGET + 'index.html'
BUDGET_CREATE = TEMPLATE_BUDGET + 'create.html'


def index(request):
    today = datetime.today()
    # The `budget` variable will strore all category with budget for the
    # month of today.month(). Has the budget_limit.
    budgets = Budget.objects.select_related('category').filter(
        month=today.month, year=today.year
    )
    # Get all the expenses for this month.
    expenses = Ledger.objects.values('category').annotate(
        total_expense=Sum('amount')
    ).filter(date_created__month=today.month)
    # Only get the expense whose category has budget set.
    with_budget_set = expenses.filter(category__budget__in=budgets)
    # Loop through the budgets.
    budget_info_list = []
    for with_budget in with_budget_set:
        for budget in budgets:
            if with_budget.get("category") == budget.category.pk:
                budget_info_list.append(
                    {
                        'category_id': budget.category.pk,
                        'category_name': budget.category.category_name,
                        'budget_limit': budget.budget_limit,
                        'spent': with_budget.get("total_expense"),
                        'remaining': budget.budget_limit
                                    - with_budget.get("total_expense"),
                    }
                )
            else:
                budget_info_list.append(
                    {
                        'category_id': budget.category.pk,
                        'category_name': budget.category.category_name,
                        'budget_limit': budget.budget_limit,
                        'spent': 0,
                        'remaining': 0,
                    }
                )
    print(with_budget_set)
    print(budget_info_list)
    context = {
        'budget_info_list': budget_info_list,
    }
    if budgets:
        categories = Category.objects.filter(
            category_type='expense'
        )
        categories = categories.exclude(budget__in=budgets)
        context.update({
            'categories': categories,
        })
    else:
        categories = Category.expenses()
        context.update({
            'categories': categories,
        })

    return render(request, BUDGET_INDEX, context)


@transaction.atomic
def create(request, pk):
    if request.method == 'GET':
        try:
            category = Category.objects.filter(
                pk=pk, category_type='expense'
            ).get()
            form = BudgetForm()
            this_month = datetime.today().strftime("%B %Y")
            context = {
                'category': category,
                'form': form,
                'this_month': this_month,
            }
            return render(request, BUDGET_CREATE, context)
        except ObjectDoesNotExist:
            raise Http404("Category does not exist")

    if request.method == 'POST':
        try:
            category = Category.objects.filter(
                pk=pk, category_type='expense'
            ).get()
            form = BudgetForm(request.POST)
            this_month = datetime.today()
            context = {
                'category': category,
                'form': form,
                'this_month': this_month.strftime("%B %Y"),
            }

            if form.is_valid():
                budget_limit = form.cleaned_data['budget_limit']
                Budget.objects.create(
                    category=category,
                    budget_limit=budget_limit,
                    month=this_month.month,
                    year=this_month.year,
                )
                messages.success(request, 'Budget Set Successfully!')
                return redirect(reverse('the_budget:budget'))
            else:
                return render(request, BUDGET_CREATE, context)
        except ObjectDoesNotExist:
            raise Http404("Category does not exist")