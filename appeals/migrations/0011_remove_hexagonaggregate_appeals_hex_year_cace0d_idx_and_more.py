# Generated by Django 5.2 on 2025-04-03 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("appeals", "0010_hexagonaggregate"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="hexagonaggregate",
            name="appeals_hex_year_cace0d_idx",
        ),
        migrations.RemoveIndex(
            model_name="hexagonaggregate",
            name="appeals_hex_month_e40a92_idx",
        ),
        migrations.AlterField(
            model_name="hexagonaggregate",
            name="year",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name="hexagonaggregate",
            index=models.Index(
                fields=["year", "month"], name="appeals_hex_year_16fa10_idx"
            ),
        ),
    ]
