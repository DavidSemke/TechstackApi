# Generated by Django 5.2.1 on 2025-06-01 03:46

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0003_alter_profile_bio"),
    ]

    operations = [
        migrations.RenameField(
            model_name="profile",
            old_name="user",
            new_name="owner",
        ),
    ]
