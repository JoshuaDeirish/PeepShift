from django.db import models
from django.conf import settings
# Create your models here.

class WasteReason(models.TextChoices):
    SPOILAGE = "spoilage", "Spoilage"
    PREP_ERROR = "prep_error", "Prep error"
    CUSTOMER_RETURN = "customer_return", "Customer return"
    EXPIRED = "expired", "Expired"
    OVER_PRODUCTION = "over_production", "Over production"
    OTHER = "other", "Other"

class WasteItem(models.Model):
      name = models.CharField(max_length=150)
      unit = models.CharField(max_length=50)
      cost_per_unit = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True) #st_per_unit
      is_active = models.BooleanField(default=True)
      location = models.ForeignKey(
          'core.Location', on_delete=models.PROTECT, related_name='waste_items'
      )
      class Meta:
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=("location", "name"), name="unique_waste_item_per_location"
            )
        ]
      def __str__(self):
          return self.name

class WasteEntry(models.Model):
    location = models.ForeignKey(
        "core.Location", on_delete=models.PROTECT, related_name="waste_entries"
    )
    item = models.ForeignKey(
        WasteItem, on_delete=models.PROTECT, related_name="entries"
    )
    quantity = models.DecimalField(max_digits=8, decimal_places=2)
    reason = models.CharField(
        max_length=32, choices=WasteReason.choices, default=WasteReason.OTHER
    )
    cost_at_entry = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    business_date = models.DateField()
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="waste_entries"
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ("-business_date", "-recorded_at")
        indexes = [
            models.Index(fields=("location", "business_date")),
        ]

    def __str__(self):
        return f"{self.quantity} {self.item.unit} {self.item.name}"