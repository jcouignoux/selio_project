# Generated by Django 3.2.5 on 2021-07-11 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_ouvrage_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ouvrage',
            name='picture',
            field=models.FileField(null=True, upload_to=''),
        ),
    ]
