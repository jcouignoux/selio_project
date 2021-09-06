# Generated by Django 3.2.5 on 2021-09-03 21:32

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('W', 'En attente de validation'), ('K', 'Contacté'), ('P', 'Payée'), ('S', 'Expédiée'), ('C', 'Annulée')], default='W', max_length=1, null=True, verbose_name='Statut de la commande'), size=None),
        ),
    ]