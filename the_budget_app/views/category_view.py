from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from django.http import Http404

from ..models import Category
from ..forms import CategoryForm


# Constant configurations for view.
TEMPLATE_CATEGORY = 'the_budget_app/category/'
# Template Accounts
CATEGORY_INDEX = TEMPLATE_CATEGORY + 'index.html'
CATEGORY_CREATE = TEMPLATE_CATEGORY + 'create.html'
CATEGORY_EDIT = TEMPLATE_CATEGORY + 'edit.html'


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


def edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if category.editable == False:
        raise Http404("Category does not exist")
    if request.method == 'GET':
        form = CategoryForm(initial={
            'category_type': category.category_type,
            'category_name': category.category_name
        })
        context = {
            'form': form,
            'category_id': category.pk,
        }
        return render(request, CATEGORY_EDIT, context)

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        context = {
            'form': form,
            'category_id': category.pk,
        }
        if form.is_valid():
            if form.has_changed():
                category_type = form.cleaned_data['category_type']
                category_name = form.cleaned_data['category_name']

                category.category_type=category_type
                category.category_name=category_name
                category.save()
            else:
                pass

            messages.success(request, 'Category Saved Successfully!')
            return redirect(reverse('the_budget:category'))
        else:
            context.update({'error':'ValidationError'})
            return render(request, CATEGORY_EDIT, context)


@transaction.atomic
def delete(request, pk):
    if request.method == 'POST':
        category = get_object_or_404(Category, pk=pk)
        category.delete()

        messages.success(request, 'Deleted Successfully!')
        return redirect(reverse('the_budget:category'))