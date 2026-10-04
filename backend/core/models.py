from django.conf import settings
from django.db import models


class Loft(models.Model):
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=200, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


class ClothRoll(models.Model):
    STATUS_RAW = "raw"
    STATUS_DIPPING = "dipping"
    STATUS_CURED = "cured"
    STATUS_CHOICES = [
        (STATUS_RAW, "原布"),
        (STATUS_DIPPING, "浸渍中"),
        (STATUS_CURED, "已固化"),
    ]

    loft = models.ForeignKey(Loft, on_delete=models.CASCADE, related_name="rolls")
    roll_code = models.CharField(max_length=40)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_RAW)
    fabric_weight_gsm = models.PositiveIntegerField(default=380)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["loft_id", "roll_code"]
        constraints = [
            models.UniqueConstraint(
                fields=["loft", "roll_code"],
                name="uniq_roll_code_per_loft",
            )
        ]

    def __str__(self):
        return f"{self.loft.name}/{self.roll_code}"


class DipRun(models.Model):
    roll = models.ForeignKey(ClothRoll, on_delete=models.CASCADE, related_name="dip_runs")
    started_at = models.DateTimeField()
    resin_pct = models.DecimalField(max_digits=5, decimal_places=2)
    cure_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"Dip@{self.roll_id} {self.started_at}"


class GsmBandSettings(models.Model):
    """克重色带分界（全台唯一一行；后写成功的一版覆盖先写）。

    分档规则（整数克重 gsm）：
      gsm <= light_max  → 轻档 light
      gsm >= heavy_min  → 重档 heavy
      其余              → 中档 medium
    """

    BAND_LIGHT = "light"
    BAND_MEDIUM = "medium"
    BAND_HEAVY = "heavy"

    DEFAULT_LIGHT_MAX = 400
    DEFAULT_HEAVY_MIN = 440

    light_max = models.PositiveIntegerField(default=DEFAULT_LIGHT_MAX)
    heavy_min = models.PositiveIntegerField(default=DEFAULT_HEAVY_MIN)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta:
        verbose_name = "克重色带分界"
        verbose_name_plural = "克重色带分界"

    def __str__(self):
        return f"轻≤{self.light_max} / 重≥{self.heavy_min}"

    @classmethod
    def get_solo(cls):
        """取唯一设置行；不存在时按出厂默认创建。"""
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "light_max": cls.DEFAULT_LIGHT_MAX,
                "heavy_min": cls.DEFAULT_HEAVY_MIN,
            },
        )
        return obj

    def band_for(self, gsm) -> str:
        gsm = int(gsm)
        if gsm <= self.light_max:
            return self.BAND_LIGHT
        if gsm >= self.heavy_min:
            return self.BAND_HEAVY
        return self.BAND_MEDIUM
