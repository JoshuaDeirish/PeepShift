from django.conf import settings
from django.db import models


class EquipmentType(models.TextChoices):
    FRIDGE = "fridge", "Fridge"
    FREEZER = "freezer", "Freezer"
    WALK_IN = "walk_in", "Walk-in"
    PREP_TABLE = "prep_table", "Prep table"
    OTHER = "other", "Other"


class Equipment(models.Model):
    location = models.ForeignKey(
        "core.Location", on_delete=models.PROTECT, related_name="equipment"
    )
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=32, choices=EquipmentType.choices, default=EquipmentType.FRIDGE
    )
    min_temp = models.DecimalField(max_digits=5, decimal_places=2)
    max_temp = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=("location", "name"), name="unique_equipment_per_location"
            )
        ]

    def __str__(self):
        return self.name


class TemperatureReading(models.Model):
    location = models.ForeignKey(
        "core.Location", on_delete=models.PROTECT, related_name="temperature_readings"
    )
    equipment = models.ForeignKey(
        Equipment, on_delete=models.PROTECT, related_name="readings"
    )
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    business_date = models.DateField()
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="temperature_readings",
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    corrective_action = models.TextField(blank=True)

    class Meta:
        ordering = ("-business_date", "-recorded_at")
        indexes = [
            models.Index(fields=("equipment", "business_date")),
        ]

    @property
    def is_out_of_range(self):
        return (
            self.temperature < self.equipment.min_temp
            or self.temperature > self.equipment.max_temp
        )

    def __str__(self):
        return f"{self.equipment} — {self.temperature}"