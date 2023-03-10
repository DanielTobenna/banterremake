# Generated by Django 3.2 on 2023-02-19 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banterapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment_id',
            name='portfolio_returns',
            field=models.FloatField(blank=True, default=0.195, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='roi',
            field=models.FloatField(default=0.195, null=True),
        ),
    ]
