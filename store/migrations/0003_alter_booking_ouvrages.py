# Generated by Django 3.2.5 on 2021-08-30 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_booking_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='ouvrages',
            field=models.JSONField(),
        ),
    ]