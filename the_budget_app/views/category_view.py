from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db import transaction

from ..models import Category


# Constant configurations for view.
TEMPLATE_CATEGORY = 'the_budget_app/category/'
# Template Accounts
CATEGORY_INDEX = TEMPLATE_CATEGORY + 'index.html'


def index(request):
    expenses = Category.expenses()
    incomes = Category.incomes()
    context = {
        'expenses': expenses,
        'incomes': incomes,
    }

    return render(request, CATEGORY_INDEX, context)