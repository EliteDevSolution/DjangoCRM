# Generated by Django 3.0.5 on 2020-04-28 02:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0025_auto_20200428_0930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='agm',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
