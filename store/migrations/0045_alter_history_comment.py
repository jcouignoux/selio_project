# Generated by Django 3.2.5 on 2021-07-30 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0044_alter_history_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='history',
            name='comment',
            field=models.CharField(max_length=10, null=True, verbose_name='Commentaire'),
        ),
    ]
