# Generated by Django 3.2.5 on 2021-07-30 15:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0037_alter_ouvrage_note'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vente',
            name='date',
            field=models.DateField(blank=True, default=datetime.datetime.now),
        ),
    ]
