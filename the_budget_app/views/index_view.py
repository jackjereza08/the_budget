from django.shortcuts import render


TEMPLATE = 'the_budget_app'


def index(response):
    context = {'hello': 'The Budget App'}
    return render(response, TEMPLATE + '/index.html', context)