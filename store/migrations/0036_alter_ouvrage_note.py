# Generated by Django 3.2.5 on 2021-07-27 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0035_history'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ouvrage',
            name='note',
            field=models.CharField(blank=True, max_length=2000, null=True, verbose_name='Note'),
        ),
    ]