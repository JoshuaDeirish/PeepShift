from django.db import models
from django.conf import settings
# Create your models here.

class Station(models.Model):
      location = models.ForeignKey(
            'core.Location', on_delete=models.PROTECT, related_name='stations'
            )
      name = models.CharField(max_length=100)
      is_active = models.BooleanField(default=True)

      class Meta:
            ordering = ('name',)
            constraints = [
                  models.UniqueConstraint(
                        fields=('location', 'name'),
                        name='unique_station_per_location',
                  )
            ]

      def __str__(self):
            return self.name
      
class ChecklistTemplate(models.Model):
    location = models.ForeignKey(
        "core.Location", on_delete=models.PROTECT, related_name="checklist_templates"
    )
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class TemplateVersion(models.Model):
    template = models.ForeignKey(
        ChecklistTemplate, on_delete=models.PROTECT, related_name="versions"
    )
    version_number = models.PositiveIntegerField()
    published_at = models.DateTimeField(null=True, blank=True)
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="published_versions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-version_number",)
        constraints = [
            models.UniqueConstraint(
                fields=("template", "version_number"), name="unique_version_per_template"
            )
        ]

    @property
    def is_published(self):
        return self.published_at is not None

    def __str__(self):
        return f"{self.template.name} v{self.version_number}"


class TemplateItem(models.Model):
    version = models.ForeignKey(
        TemplateVersion, on_delete=models.CASCADE, related_name="items"
    )
    station = models.ForeignKey(
        Station, on_delete=models.PROTECT, related_name="template_items"
    )
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("station", "order")

    def __str__(self):
        return self.text


class ChecklistRun(models.Model):
    version = models.ForeignKey(
        TemplateVersion, on_delete=models.PROTECT, related_name="runs"
    )
    station = models.ForeignKey(
        Station, on_delete=models.PROTECT, related_name="runs"
    )
    business_date = models.DateField()
    signed_off_at = models.DateTimeField(null=True, blank=True)
    signed_off_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="signed_off_runs",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-business_date",)
        constraints = [
            models.UniqueConstraint(
                fields=("version", "station", "business_date"),
                name="unique_run_per_station_per_day",
            )
        ]

    @property
    def is_signed_off(self):
        return self.signed_off_at is not None

    def __str__(self):
        return f"{self.station} — {self.business_date}"


class ItemCompletion(models.Model):
    run = models.ForeignKey(
        ChecklistRun, on_delete=models.CASCADE, related_name="completions"
    )
    item = models.ForeignKey(
        TemplateItem, on_delete=models.PROTECT, related_name="completions"
    )
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="completions"
    )
    completed_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ("item__order",)
        constraints = [
            models.UniqueConstraint(
                fields=("run", "item"), name="unique_completion_per_item_per_run"
            )
        ]

    def __str__(self):
        return f"{self.item} by {self.completed_by}"