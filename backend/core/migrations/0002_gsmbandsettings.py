from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="GsmBandSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("light_max_gsm", models.PositiveIntegerField(default=400)),
                ("heavy_min_gsm", models.PositiveIntegerField(default=440)),
                ("updated_by", models.CharField(blank=True, default="", max_length=150)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "克重色带分界",
            },
        ),
    ]
