# Generated by Django 3.2.5 on 2021-07-14 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_alter_ouvrage_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ouvrage',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='store/static/store/couv'),
        ),
    ]
