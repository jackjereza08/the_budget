from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils import timezone

from .models import Account, Category, Ledger
from .forms import (
    IncomeForm, ExpenseForm, TransferForm, BudgetForm, CategoryForm
    )


# Accounts
PATH_ACCOUNTS = '/accounts'
PATH_ACCOUNT_CREATE = PATH_ACCOUNTS + '/create'

# Records
PATH_RECORD = '/records'
PATH_INCOME = '/new-record/income'
PATH_EXPENSE = '/new-record/expense'
PATH_TRANSFER = '/new-record/transfer'
PATH_DELETE_RECORD = '/record/delete'


def create_account(name, splitting_percent, initial_amount):
    return Account.objects.create(
        account_name=name,
        splitting_percent=splitting_percent,
        amount=initial_amount
    )


def create_category(category_type: str, name: str, editable: bool):
    return Category.objects.create(
        category_type=category_type,
        category_name=name,
        editable=editable
    )


# Create your tests here.
class AccountTests(TestCase):
    """
    Tests the Model and View of `Account`.
    """
    def test_view_if_save_splitting_percent_gt_100(self):
        """
        If client inserts splitting_percent greater than 100 then it
        should not save in the database and will not redirect to
        `/accounts`.
        """
        response = self.client.post(
            PATH_ACCOUNT_CREATE,
            {
                'account_name': 'Test',
                'splitting_percent': 101,
                'initial_amount': 0
            },
        )
        self.assertIs(response.status_code==302, False)
        
    def test_view_if_values_are_valid(self):
        """
        If client inserts correct value then it will save and redirects
        to `/accounts`.
        """
        response = self.client.post(
            PATH_ACCOUNT_CREATE,
            {
                'account_name': 'Test',
                'splitting_percent': 100,
                'initial_amount': 0
            },
        )
        self.assertIs(response.status_code==302, True)
        self.assertRedirects(response, PATH_ACCOUNTS, 302, 200)

    def test_view_if_split_sum_equals_100(self):
        """
        If the sum of splitting_percent is equals to 100, the context
        `is_split_disabled` should return True and the splitting_percent
        field is not displayed.
        """
        create_account('Needs', 50, 0)
        create_account('Wants', 30, 0)
        create_account('Savings', 20, 0)

        response = self.client.get(PATH_ACCOUNT_CREATE)

        self.assertEqual(response.context['is_split_disabled'], True)
        self.assertNotContains(response, 'Splitting Percent')

        response = self.client.post(
            PATH_ACCOUNT_CREATE,
            {
                'account_name':'Test',
                'initial_amount': '0'
            },
        )

        self.assertRedirects(response, PATH_ACCOUNTS, 302, 200)

        response = self.client.post(
            PATH_ACCOUNT_CREATE,
            {
                'account_name': 'Test',
                'splitting_percent': 20,
                'initial_amount': 0
            },
        )

        self.assertEqual(response.context['error'],'ValidationError')

    def test_view_if_split_sum_lt_100(self):
        """
        Test the view's logic if the sum of splitting percent is less
        than 100.
        """
        create_account('Needs', 50, 0)
        create_account('Wants', 30, 0)

        response = self.client.get(PATH_ACCOUNT_CREATE)

        self.assertContains(response, 'Splitting Percent')

        response = self.client.post(
            PATH_ACCOUNT_CREATE,
            {
                'account_name': 'Test',
                'splitting_percent': 100,
                'initial_amount': 0
            },
        )

        self.assertEqual(response.context['error'], 'ValidationError')

        response = self.client.post(
            PATH_ACCOUNT_CREATE,
            {
                'account_name': 'Test',
                'splitting_percent': 20,
                'initial_amount': 0
            },
        )
        self.assertRedirects(response, PATH_ACCOUNTS, 302, 200)


class RecordTest(TestCase):
    """
    Test the record view, the add income, expense, and transfer.
    """
    def setUp(self):
        create_account('Needs', 50, 0)
        create_account('Wants', 30, 100)
        create_account('Savings', 20, 100)
        create_category('income', 'Sale', True)
        create_category('expense', 'Food', True)
        # Transfer category should be False. But for the sake of testing,
        # I changed it to True just to save this below category.
        create_category('transfer', 'Transfer', True)

    def test_record_index_page(self):
        response = self.client.get(
            PATH_RECORD,
        )

        self.assertIs(response.status_code, 200)
        self.assertTemplateUsed(response, 'the_budget_app/records/records.html')

    def test_record_add_income_no_data(self):
        response = self.client.post(
            PATH_INCOME,

        )

        self.assertTemplateUsed(response, 'the_budget_app/new_record/index.html')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error'], "ValidationError")

    def test_record_add_expense_no_data(self):
        response = self.client.post(
            PATH_EXPENSE,

        )

        self.assertTemplateUsed(response, 'the_budget_app/new_record/index.html')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error'], "ValidationError")
    
    def test_record_add_transfer_no_data(self):
        response = self.client.post(
            PATH_TRANSFER,

        )

        self.assertTemplateUsed(response, 'the_budget_app/new_record/index.html')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error'], "ValidationError")

    def test_record_add_income(self):
        """
        Checks the validity of the data entered by the user when adding
        new income.
        """
        # Valid data.
        response = self.client.post(
            PATH_INCOME,
            {
                'account': 1,
                'category': 1,
                'amount': 10.99,
                'note': '',
                'date': '2023-5-15',
                'time': '15:15:00',
            }
        )

        account = Account.objects.get(pk=1)
        ledger = Ledger.objects.all().last()

        self.assertRedirects(response, PATH_RECORD, 302, 200)
        self.assertEqual(account.amount, 10.99)
        self.assertEqual(ledger.amount, 10.99)

        # Invalid data.
        response = self.client.post(
            PATH_INCOME,
            {
                'account': 5,
                'category': 5,
                'amount': 133210.4566,
                'note': '',
                'date': '15-05-202',
                'time': '115:00',
            }
        )

        self.assertTemplateUsed(
            response, 'the_budget_app/new_record/index.html'
        )
        self.assertTemplateNotUsed(
            response, 'the_budget_app/records/records.html'
        )
        self.assertEqual(response.context['error'], "ValidationError")


    def test_record_add_expense(self):
        """
        Checks the validity of the data entered by the user when adding
        new expense.
        """
        # Valid data.
        response = self.client.post(
            PATH_EXPENSE,
            {
                'account': 2,
                'category': 2,
                'amount': 100,
                'note': '',
                'date': '2023-5-29',
                'time': '15:15:00',
            }
        )

        account = Account.objects.get(pk=2)
        ledger = Ledger.objects.all().last()

        self.assertRedirects(response, PATH_RECORD, 302, 200)
        self.assertEqual(account.amount, 0)
        self.assertEqual(ledger.amount, 100)

        # Invalid amount.
        response = self.client.post(
            PATH_EXPENSE,
            {
                'account': 2,
                'category': 2,
                'amount': 101,
                'note': '',
                'date': '15-05-20',
                'time': '15:00',
            }
        )

        self.assertTemplateUsed(
            response, 'the_budget_app/new_record/index.html'
        )
        self.assertTemplateNotUsed(
            response, 'the_budget_app/records/records.html'
        )
        self.assertEqual(response.context['error'], "ValidationError")
        # Invalid data.
        response = self.client.post(
            PATH_EXPENSE,
            {
                'account': 7,
                'category': 7,
                'amount': 101,
                'note': '',
                'date': '15-0e5-20',
                'time': '1235:0230',
            }
        )

        self.assertTemplateUsed(
            response, 'the_budget_app/new_record/index.html'
        )
        self.assertTemplateNotUsed(
            response, 'the_budget_app/records/records.html'
        )
        self.assertEqual(response.context['error'], "ValidationError")


    def test_record_add_transfer(self):
        """
        Checks the validity of the data entered by the user when adding
        new transfer.
        """
        # Valid data.
        response = self.client.post(
            PATH_TRANSFER,
            {
                'account': 2,
                'to_account': 1,
                'amount': 50,
                'note': '',
                'date': '2023-05-29',
                'time': '15:15:00',
            }
        )

        account = Account.objects.get(pk=2)
        to_account = Account.objects.get(pk=1)
        ledger = Ledger.objects.all().last()

        self.assertRedirects(response, PATH_RECORD, 302, 200)
        self.assertEqual(account.amount, 50)
        self.assertEqual(to_account.amount, 50)
        self.assertEqual(ledger.amount, 50)

        # Invalid data.
        response = self.client.post(
            PATH_TRANSFER,
            {
                'account': 2,
                'account': 2,
                'amount': 101,
                'note': '',
                'date': '15-05-20',
                'time': '15:00',
            }
        )

        self.assertTemplateUsed(
            response, 'the_budget_app/new_record/index.html'
        )
        self.assertTemplateNotUsed(
            response, 'the_budget_app/records/records.html'
        )
        self.assertEqual(response.context['error'], "ValidationError")


    def test_delete_record(self):
        """
        Test delete record.
        """
        # add new income.
        response = self.client.post(
            PATH_INCOME,
            {
                'account': 1,
                'category': 1,
                'amount': 100,
                'note': '',
                'date': '2023-5-15',
                'time': '15:15:00',
            }
        )
        self.assertEqual(response.status_code, 302)
        # add new expense.
        response = self.client.post(
            PATH_EXPENSE,
            {
                'account': 1,
                'category': 2,
                'amount': 50,
                'note': '',
                'date': '2023-5-15',
                'time': '15:15:00',
            }
        )
        self.assertEqual(response.status_code, 302)
        # add new transfer.
        response = self.client.post(
            PATH_TRANSFER,
            {
                'account': 2,
                'to_account': 1,
                'amount': 50,
                'note': '',
                'date': '2023-5-15',
                'time': '15:15:00',
            }
        )
        self.assertEqual(response.status_code, 302)
        record = Ledger.objects.all()
        account = Account.objects.all()
        print(record)
        print(account)
        self.assertEqual(Ledger.objects.count(), 3)
        self.assertEqual(record[0].amount, 100)
        self.assertEqual(record[1].amount, 50)
        self.assertEqual(record[2].amount, 50)
        
        self.assertEqual(account[0].amount, 100)
        self.assertEqual(account[1].amount, 50)
        self.assertEqual(account[2].amount, 100)

        response = self.client.post(
            PATH_DELETE_RECORD + '/1'
        )
        self.assertRedirects(response, PATH_RECORD, 302, 200)
        response = self.client.post(
            PATH_DELETE_RECORD + '/2'
        )
        self.assertRedirects(response, PATH_RECORD, 302, 200)
        response = self.client.post(
            PATH_DELETE_RECORD + '/3'
        )
        self.assertRedirects(response, PATH_RECORD, 302, 200)
        record = Ledger.objects.all()
        account = Account.objects.all()
        print(record)
        print(account)
        self.assertEqual(Ledger.objects.count(), 0)
        self.assertEqual(account[0].amount, 0)
        self.assertEqual(account[1].amount, 100)
        self.assertEqual(account[2].amount, 100)


class FormTest(TestCase):
    """
    Test the forms.
    """
    def setUp(self):
        create_account('Needs', 50, 0)
        create_account('Wants', 30, 100)
        create_account('Savings', 20, 0)
        create_category('income', 'Sale', True)
        create_category('expense', 'Food', True)

    def test_income_form(self):
        """Test the IncomeForm"""
        data = {
            'account': 1,
            'category': 1,
            'amount': 10.99,
            'note': '',
            'date': '2023-5-15',
            'time': '15:15:00',
        }
        form = IncomeForm(data)

        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())

        data = {
            'account': 5,
            'category': 2,
            'amount': 10.9943,
            'note': '',
            'date': '2023-5',
            'time': '1534:00',
        }
        form = IncomeForm(data)

        self.assertTrue(form.is_bound)
        self.assertFalse(form.is_valid())

    def test_expense_form(self):
        """Test the ExpenseForm"""
        data = {
            'account': 2,
            'category': 2,
            'amount': 10.99,
            'note': '',
            'date': '2023-5-15',
            'time': '15:15:00',
        }
        form = ExpenseForm(data)

        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())

        data = {
            'account': 2,
            'category': 1,
            'amount': 10.9943,
            'note': '',
            'date': '2023-5',
            'time': '1534:00',
        }
        form = ExpenseForm(data)

        self.assertTrue(form.is_bound)
        self.assertFalse(form.is_valid())

    def test_transfer_form(self):
        """Test the TransferForm"""
        data = {
            'account': 2,
            'to_account': 1,
            'amount': 10.99,
            'note': '',
            'date': '2023-5-15',
            'time': '15:15:00',
        }
        form = TransferForm(data)

        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())

        data = {
            'account': 2,
            'to_account': 1,
            'amount': 10.9943,
            'note': '',
            'date': '2023-5',
            'time': '1534:00',
        }
        form = TransferForm(data)

        self.assertTrue(form.is_bound)
        self.assertFalse(form.is_valid())

        data = {
            'account': 2,
            'to_account': 2,
            'amount': 10.99,
            'note': '',
            'date': '2023-5-15',
            'time': '15:15:00',
        }
        form = TransferForm(data)

        self.assertTrue(form.is_bound)
        self.assertFalse(form.is_valid())

    def test_budget_form(self):
        """Test the BudgetForm"""
        data1 = {
            'budget_limit': 100
        }
        data2 = {
            'budget_limit': 0
        }
        data3 = {
            'budget_limit': 123456789.102345
        }

        form1 = BudgetForm(data1)
        form2 = BudgetForm(data2)
        form3 = BudgetForm(data3)

        self.assertTrue(form1.is_valid())
        self.assertFalse(form2.is_valid())
        self.assertFalse(form3.is_valid())

    def test_category_form(self):
        data = [
            { #Valid
                'category_type': 'income',
                'category_name': 'Sale',
            },
            { #Valid
                'category_type': 'expense',
                'category_name': 'Load',
            },
            { #Invalid
                'category_type': 'incme',
                'category_name': 'Sale',
            },
            { #Invalid
                'category_type': '',
                'category_name': 'Sale',
            },
            { #Invalid
                'category_type': 'income',
                'category_name': '',
            },
            { #Invalid
                'category_type': '',
                'category_name': '',
            },
        ]
        for c in range(len(data[:2])):
            form = CategoryForm(data[c])
            self.assertTrue(form.is_valid())

        for c in range(2, len(data[2:])):
            form = CategoryForm(data[c])
            self.assertFalse(form.is_valid())


class ModelTest(TestCase):
    """
    Test the models.
    """
    def test_category_if_transfer_and_from_deleted_account_editable(self):
        pass
        """
        Check the custom save function to make sure the `transfer` and
        `from deleted account` data will not change.
        """
        # Code below passed the test as creating a category that has
        # editable set to False.
        # The category `from deleted account` and `Transfer` will be in
        # system's default data in the database.
        
        # create_category('transfer','Transfer', False)

        # c = Category.objects.count()

        # self.assertEqual(c, 1)
        
        # c = Category.objects.get(pk=1) #transfer
        # self.assertEqual(c.editable, False)
        # c.editable = True
        # c.save()
        
        # self.assertRaises(ValidationError)
        # self.assertEqual(c.editable, False)
