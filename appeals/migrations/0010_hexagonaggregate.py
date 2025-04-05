# Generated by Django 5.2 on 2025-04-03 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("appeals", "0009_appeal_district_boundary_appeal_district_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="HexagonAggregate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("hexagon_id", models.CharField(max_length=255)),
                ("year", models.IntegerField()),
                ("month", models.IntegerField(blank=True, null=True)),
                ("count", models.IntegerField()),
                ("types", models.JSONField()),
                ("boundary_coords", models.JSONField()),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["hexagon_id"], name="appeals_hex_hexagon_4d51fc_idx"
                    ),
                    models.Index(fields=["year"], name="appeals_hex_year_cace0d_idx"),
                    models.Index(fields=["month"], name="appeals_hex_month_e40a92_idx"),
                ],
            },
        ),
    ]
