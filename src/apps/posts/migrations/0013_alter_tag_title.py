# Generated by Django 5.2.1 on 2025-06-21 04:22

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0012_remove_reaction_unique_owner_post_comment_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tag",
            name="title",
            field=models.CharField(
                max_length=20,
                unique=True,
                validators=[
                    django.core.validators.MinLengthValidator(1),
                    django.core.validators.RegexValidator(
                        "^[-\\dA-Za-z]*$",
                        message="Tag title must only contain letters, numbers, and hyphens.",
                    ),
                ],
            ),
        ),
    ]
