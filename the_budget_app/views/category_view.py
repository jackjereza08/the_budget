from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db import transaction

from ..models import Category
from ..forms import CategoryForm


# Constant configurations for view.
TEMPLATE_CATEGORY = 'the_budget_app/category/'
# Template Accounts
CATEGORY_INDEX = TEMPLATE_CATEGORY + 'index.html'
CATEGORY_CREATE = TEMPLATE_CATEGORY + 'create.html'


def index(request):
    expenses = Category.expenses()
    incomes = Category.incomes()
    context = {
        'expenses': expenses,
        'incomes': incomes,
    }

    return render(request, CATEGORY_INDEX, context)


def create(request):
    if request.method == 'GET':
        form = CategoryForm()
        context = {
            'form': form
        }
        return render(request, CATEGORY_CREATE, context)

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        context = {
            'form': form
        }
        if form.is_valid():
            category_type = form.cleaned_data['category_type']
            category_name = form.cleaned_data['category_name']

            Category.objects.create(
                category_type=category_type,
                category_name=category_name
            )

            messages.success(request, 'Category Added Successfully!')
            return redirect(reverse('the_budget:category'))
        else:
            context.update({'error':'ValidationError'})
            return render(request, CATEGORY_CREATE, context)