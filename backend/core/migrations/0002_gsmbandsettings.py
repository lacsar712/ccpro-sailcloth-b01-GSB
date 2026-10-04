import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def create_default_settings(apps, schema_editor):
    GsmBandSettings = apps.get_model("core", "GsmBandSettings")
    GsmBandSettings.objects.get_or_create(
        pk=1, defaults={"light_max": 400, "heavy_min": 440}
    )


def drop_default_settings(apps, schema_editor):
    GsmBandSettings = apps.get_model("core", "GsmBandSettings")
    GsmBandSettings.objects.filter(pk=1).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
                ("light_max", models.PositiveIntegerField(default=400)),
                ("heavy_min", models.PositiveIntegerField(default=440)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "克重色带分界",
                "verbose_name_plural": "克重色带分界",
            },
        ),
        migrations.RunPython(create_default_settings, drop_default_settings),
    ]
