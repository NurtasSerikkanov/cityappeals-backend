# Generated by Django 5.2 on 2025-04-02 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("appeals", "0003_alter_appeal_address_alter_appeal_location"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appeal",
            name="hexagon_id",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="appeal",
            name="title",
            field=models.CharField(max_length=1024),
        ),
    ]
