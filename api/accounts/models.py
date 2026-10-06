from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class UserRole(models.TextChoices):
    STAFF = "Staff", "staff"
    SUPERVISOR = "Supervisor", "supervisor"
    MANAGER = "Manager", "manager"
    ADMIN = "Admin", "admin"
class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Users must have a phone number")

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ADMIN)
        extra_fields.setdefault("must_change_pin", False)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(phone, password, **extra_fields)


class User(AbstractUser):
    username = None
    phone = PhoneNumberField(unique=True)
    must_change_pin = models.BooleanField(default=True)
    role = models.CharField(
        max_length=32, choices=UserRole.choices, default=UserRole.STAFF
    )
    # location = models.ForeignKey("core.Location", on_delete=models.SET_NULL, null=True)
    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.phone)