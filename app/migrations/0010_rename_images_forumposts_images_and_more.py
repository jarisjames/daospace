# Generated by Django 5.0.1 on 2024-01-24 01:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_rename_total_emoji_reactions_forumposts_totalemojireactions'),
    ]

    operations = [
        migrations.RenameField(
            model_name='forumposts',
            old_name='images',
            new_name='Images',
        ),
        migrations.RenameField(
            model_name='forumposts',
            old_name='links',
            new_name='Links',
        ),
        migrations.RenameField(
            model_name='forumposts',
            old_name='role',
            new_name='Role',
        ),
        migrations.RenameField(
            model_name='forumposts',
            old_name='total_replies',
            new_name='TotalReplies',
        ),
    ]