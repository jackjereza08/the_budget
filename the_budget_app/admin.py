from django.contrib import admin

from .models import Account, Category, Budget


class BudgetInline(admin.StackedInline):
    model = Budget
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    inlines = [BudgetInline]


# Register your models here.
admin.site.register(Account)
admin.site.register(Category, CategoryAdmin)