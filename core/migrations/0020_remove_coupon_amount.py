# Generated by Django 3.1.4 on 2020-12-28 12:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20201228_1732'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coupon',
            name='amount',
        ),
    ]