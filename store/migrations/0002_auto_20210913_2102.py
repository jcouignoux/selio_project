# Generated by Django 3.2.5 on 2021-09-13 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contact',
            name='user',
        ),
        migrations.AlterField(
            model_name='booking',
            name='status',
            field=models.CharField(blank=True, choices=[('W', 'En attente de validation'), ('K', 'Contacté'), ('P', 'Payée'), ('S', 'Expédiée'), ('C', 'Annulée'), ('D', 'Annulé')], default='W', max_length=1, null=True, verbose_name='Statut de la commande'),
        ),
    ]