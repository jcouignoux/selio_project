# Generated by Django 3.2.5 on 2021-07-12 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_alter_ouvrage_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ouvrage',
            name='categories',
            field=models.ManyToManyField(related_name='ouvrages', to='store.Categorie'),
        ),
        migrations.AlterField(
            model_name='ouvrage',
            name='picture',
            field=models.ImageField(null=True, upload_to='store/couv'),
        ),
    ]
