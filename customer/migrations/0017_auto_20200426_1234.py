# Generated by Django 3.0.5 on 2020-04-26 02:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0016_requirement_order_paid'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='requirement',
            options={'ordering': ['-customer__created_date']},
        ),
    ]
