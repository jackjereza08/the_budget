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
    budget = Budget.objects.select_related('category').filter(
        month=today.month, year=today.year
    )
    expenses = Ledger.objects.values('category').annotate(
        total_expense=Sum('amount')
    ).filter(date_created__month=today.month)
    with_budget_set = expenses.filter(category__budget__in=budget)
    budget_left = []
    for b, j in zip(budget, with_budget_set):
        whats_left = b.budget_limit - j['total_expense']
        budget_left.append(whats_left)
    
    budgets_and_expense = zip(budget, budget_left)

    context = {
        'budgets': budgets_and_expense,
        'with_budget_set': with_budget_set,
    }
    if budget:
        categories = Category.objects.filter(
            category_type='expense'
        )
        categories = categories.exclude(budget__in=budget)
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