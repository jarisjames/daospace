# Generated by Django 5.0.1 on 2024-02-01 02:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_rename_id_forumposts_postid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forumposts',
            name='replies',
            field=models.TextField(),
        ),
    ]
