# Generated by Django 5.0.1 on 2024-01-24 01:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_forumposts_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='forumposts',
            old_name='total_emoji_reactions',
            new_name='TotalEmojiReactions',
        ),
    ]