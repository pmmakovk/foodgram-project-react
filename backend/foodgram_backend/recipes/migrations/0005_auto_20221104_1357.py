# Generated by Django 2.2.28 on 2022-11-04 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20221104_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, upload_to='backend/foodgram_backend/recipe/', verbose_name='Картинка'),
        ),
    ]
