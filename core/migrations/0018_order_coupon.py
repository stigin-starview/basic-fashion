# Generated by Django 3.1.4 on 2020-12-28 10:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_coupon'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='Coupon',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.coupon'),
        ),
    ]
