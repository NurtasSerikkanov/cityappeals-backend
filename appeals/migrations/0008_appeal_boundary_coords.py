# Generated by Django 5.2 on 2025-04-03 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("appeals", "0007_auto_20250403_0556"),
    ]

    operations = [
        migrations.AddField(
            model_name="appeal",
            name="boundary_coords",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
