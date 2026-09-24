from django.conf import settings
from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Location(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name="locations",
    )
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)
    timezone = models.CharField(max_length=64, default="America/Toronto")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class UserLocation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="location_links",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name="user_links",
    )
    is_primary = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "location"),
                name="unique_user_location",
            )
        ]

    def __str__(self):
        return f"{self.user} @ {self.location}"