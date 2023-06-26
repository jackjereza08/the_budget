from django.urls import path

from .views import (
    index_view as index,
    accounts_view as account,
    new_record_view as new_record,
    records_view as record,
    budget_view as budget,
)

app_name="the_budget"
urlpatterns = [
    path('', index.index, name='index'),
    path('accounts',account.index, name='account'),
    path('accounts/create', account.create, name='add_account'),
    path('accounts/edit/<int:pk>', account.edit, name='update_account'),
    path('accounts/delete/<int:pk>', account.delete, name='delete_account'),
    path('new-record/income', new_record.income, name='new_income'),
    path('new-record/expense', new_record.expense, name='new_expense'),
    path('new-record/transfer', new_record.transfer, name='new_transfer'),
    path('records', record.index, name='record'),
    path('record/detail/<int:pk>', record.detail, name='detail_record'),
    path('record/delete/<int:pk>', record.delete, name='delete_record'),
    path('budget', budget.index, name='budget'),
    path('budget/set/<int:pk>', budget.create, name='create_budget'),

]