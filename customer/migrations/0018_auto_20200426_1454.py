# Generated by Django 3.0.5 on 2020-04-26 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0017_auto_20200426_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='requirement',
            name='last_amount_paid_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='requirement',
            name='pcs',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='requirement',
            name='stc',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
