# Generated by Django 4.1.3 on 2023-05-29 05:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('the_budget_app', '0006_category_editable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ledger',
            name='to_account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='to_account', to='the_budget_app.account'),
        ),
    ]
