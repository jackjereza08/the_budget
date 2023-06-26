from datetime import datetime

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class Account(models.Model):
    account_name = models.CharField(max_length=200)
    splitting_percent = models.IntegerField(default=0)
    amount = models.FloatField(default=0)

    class Meta:
        db_table = 'account'

    def __str__(self):
        return f'{self.account_name}, {self.amount}'

    def list_of_accounts():
        return Account.objects.all()

    def amount_gt_zero():
        return Account.objects.filter(amount__gt=0)

    def get_sum_of_splitting_percent():
        total = Account.objects.aggregate(
                sum=models.Sum('splitting_percent')
            )
        if total['sum'] == None:
            return 0
        else:
            return int(total['sum'])


class Category(models.Model):
    CATEGORY_TYPE = (
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('transfer','Transfer')
    )
    category_type = models.CharField(max_length=8, choices=CATEGORY_TYPE)
    category_name = models.CharField(max_length=200)
    editable = models.BooleanField(default=True)

    class Meta:
        db_table = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return (f"{self.category_name} ({self.category_type})")

    def list_of(arg):
        return Category.objects.filter(category_type=arg)

    def get_transfer():
        return Category.objects.filter(category_type='transfer').get()

    def is_editable(self):
        category = Category.objects.get(pk=self.pk)
        return category.editable

    def expenses():
        return Category.objects.filter(category_type='expense')

    def incomes():
        return Category.objects.filter(category_type='expense', editable=True)

    def save(self, *args, **kwargs):
        # Get the original data of the object's editable.
        if self.DoesNotExist:
            super().save( *args, **kwargs)
        else:
            category = Category.objects.get(pk=self.pk)
            if category.editable == True:
                super().save( *args, **kwargs)
            else:
                raise ValidationError('CANNOT edit this data. Sorry.')


class Budget(models.Model):
    MONTH = (
        (1,'January'), (2,'February'), (3,'March'), (4,'April'),
        (5,'May'), (6,'June'), (7,'July'), (8,'August'),
        (9,'September'), (10,'October'), (11,'November'), (12,'December'),
    )

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    budget_limit = models.FloatField(default=0)
    month = models.IntegerField(validators=[
            MinValueValidator(1),
            MaxValueValidator(12),
        ],
        choices=MONTH,
        default=1,
    )
    year = models.IntegerField(validators=[
            MinValueValidator(1999),
            MaxValueValidator(9999),
        ],
        default=datetime.today().year,
    )

    class Meta:
        db_table = 'budget'

    def __str__(self):
        return str(
            (
                self.category.category_name,
                self.budget_limit,
                self.month,
                self.year
            )
        )

    def before_this_month(self):
        today = datetime.today()
        if self.year < today.year:
            return True
        elif self.year == today.year:
            if self.month < today.month:
                return True
            else:
                return False
        else:
            return False

    def list_of_budget_set():
        today = datetime.today()
        budget_set_this_month = Budget.objects.filter(
            month=today.month,
            year=today.year,
        )
        return budget_set_this_month


class Ledger(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, related_name='to_account')
    amount = models.FloatField(default=0)
    note = models.CharField(max_length=200, blank=True)
    date_created = models.DateTimeField()

    class Meta:
        db_table = 'ledger'

    def __str__(self):
        return str(
            (
                self.pk,
                self.account.account_name,
                self.category.category_name,
                self.amount,
                self.note[:6],
            )
        )
        

class AppData:
    """
    Use to reset the app's data in the database.
    """
    @staticmethod
    def reset():
        Account.objects.all().delete()
        Category.objects.all().delete()

        # Create default Accounts.
        accounts = [
            ('Needs', 50),
            ('Wants', 30),
            ('Savings', 20),
        ]

        for name, percent in accounts:
            Account.objects.create(
                account_name=name,
                splitting_percent=percent
            )
        # Create default Categories.
        incomes = (
            'Awards',
            'Coupons',
            'Grants',
            'Lottery',
            'Refunds',
            'Rental',
            'Salary',
            'Sale'
        )

        expenses = (
            'Baby',
            'Beauty',
            'Bills',
            'Car',
            'Clothing',
            'Education',
            'Electronics',
            'Entertainment',
            'Food',
            'Health',
            'Home',
            'Insurance',
            'Shopping',
            'Social',
            'Sport',
            'Tax',
            'Telephone',
            'Transportation',
        )

        Category.objects.create(
            category_type='transfer',
            category_name='Transfer',
            editable=False
        )

        Category.objects.create(
            category_type='income',
            category_name='From deleted account',
            editable=False
        )

        for income in incomes:
            Category.objects.create(
                category_type='income',
                category_name=income,
                editable=True
            )

        for expense in expenses:
            Category.objects.create(
                category_type='expense',
                category_name=expense,
                editable=True
            )