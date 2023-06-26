import datetime

from django import forms
from .models import Account, Category


class AccountForm(forms.Form):
    """
    Create and/or modify `Account` data.
    """
    account_name = forms.CharField(
        label='Account Name',
        max_length=100,
        label_suffix='',
    )
    splitting_percent = forms.IntegerField(
        label='Splitting Percent',
        max_value=100,
        min_value=0,
        required=False,
        step_size=1,
    )
    initial_amount = forms.FloatField(
        label='Initial Amount',
        min_value=0,
        required=False,
        initial=0,
        label_suffix='',
    )

    # Styling the form fields.
    account_name.widget.attrs.update({'class': 'form-control'})
    splitting_percent.widget.attrs.update({'class': 'form-control'})
    initial_amount.widget.attrs.update({'class': 'form-control'})

    def __init__(self, max_value=100, *args, **kwargs,):
        """
        Initialized the splitting_percent field max_value input based
        on the remaining splitting percent of the Accounts.
        """
        super().__init__(*args, **kwargs)
        self.fields['splitting_percent'] = forms.IntegerField(
            label='Splitting Percent',
            max_value=max_value,
            min_value=0,
            required=False,
            step_size=1,
            initial=max_value, 
            label_suffix='',
            widget=forms.NumberInput(attrs={'class':'form-control'})
        )

class DateInput(forms.DateInput):
    """
    Overriding forms.DateInput input_type from `text` to `date` to
    take advantage of the HTML5's date picker.
    """
    input_type = 'date'


class TimeInput(forms.TimeInput):
    """
    Overriding forms.TimeInput input_type from `text` to `time` to
    take advantage of the HTML5's time picker.
    """
    input_type = 'time'


class NewRecordForm(forms.Form):
    """
    Parent Class for Income, Expense, and Transfer Form.

    Field `account` and `category` is for IncomeForm and ExpenseForm.
    Field `to_account` is for TransferForm.
    """
    account = forms.ChoiceField(
        label='Account',
    )

    category = forms.ChoiceField(
        label='Category',
    )

    to_account = forms.ChoiceField(
        label='To Account',
    )

    amount = forms.DecimalField(
        label='Amount',
        min_value=0,
        max_digits=11,
        decimal_places=2,
        label_suffix='',
    )

    note = forms.CharField(
        label='Add notes',
        max_length=200,
        required=False,
        widget=forms.Textarea,
        label_suffix='',
    )

    date = forms.DateField(
        widget=DateInput,
        initial=datetime.date.today(),
        label_suffix='',
    )

    time = forms.TimeField(
        widget=TimeInput,
        initial=datetime.datetime.now(),
        label_suffix='',
    )

    # Styling the form fields.
    amount.widget.attrs.update({'class': 'form-control form-control-lg'})
    note.widget.attrs.update({'class': 'form-control', 'rows': 3})
    date.widget.attrs.update({'class': 'form-control'})
    time.widget.attrs.update({'class': 'form-control'})


def init_fields(self, category: str):
    """
    Initialized the fields for Income, Expense, Transfer.
    """
    if category == 'income':
        self.fields['account'] = forms.ChoiceField(
            choices=[
                (account.pk, f"{account.account_name} ({account.amount:.2f})")
                for account in Account.list_of_accounts()
            ],
            label_suffix='',
            widget=forms.Select(attrs={'class':'form-select'})
        )
    elif category == 'expense':
        self.fields['account'] = forms.ChoiceField(
            choices=[
                (account.pk, f"{account.account_name} ({account.amount:.2f})")
                for account in Account.amount_gt_zero()
            ],
            label_suffix='',
            widget=forms.Select(attrs={'class':'form-select'})
        )

    if category in ('income', 'expense'):
        self.fields['category'] = forms.ChoiceField(
            choices = [
                (category.pk, category.category_name)
                for category in Category.list_of(category)
            ],
            label_suffix='',
            widget=forms.Select(attrs={'class':'form-select'})
        )
    else:
        self.fields['account'] = forms.ChoiceField(
            choices=[
                (account.pk, f"{account.account_name} ({account.amount:.2f})")
                for account in Account.amount_gt_zero()
            ],
            label_suffix='',
            widget=forms.Select(attrs={'class':'form-select'})
        )
        self.fields['to_account'] = forms.ChoiceField(
            choices = [
                (account.pk, f"{account.account_name} ({account.amount:.2f})")
                for account in Account.list_of_accounts()
            ],
            label_suffix='',
            widget=forms.Select(attrs={'class':'form-select'})
        )


class IncomeForm(NewRecordForm):
    auto_split = forms.BooleanField(
        label='Auto Split',
        label_suffix='',
        required=False
    )

    auto_split.widget.attrs.update({'class': 'form-check-input'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        init_fields(self, 'income')

    to_account = None


class ExpenseForm(NewRecordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        init_fields(self, 'expense')

    to_account = None


class TransferForm(NewRecordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        init_fields(self, 'transfer')

    category = None


class BudgetForm(forms.Form):
    budget_limit = forms.DecimalField(
        label='Budget Limit',
        min_value=1,
        max_digits=11,
        decimal_places=2,
        label_suffix='',
        initial=0,
    )

    budget_limit.widget.attrs.update({'class': 'form-control'})


class CategoryForm(forms.Form):
    CATEGORY_TYPE = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    category_type = forms.ChoiceField(
        widget=forms.RadioSelect,
        label='Category Type',
        label_suffix='',
        choices=CATEGORY_TYPE,
    )
    category_name = forms.CharField(
        label='Category Name',
        label_suffix='',
        max_length=30,
    )

    category_name.widget.attrs.update({'class': 'form-control'})