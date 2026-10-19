from rest_framework import serializers
import phonenumbers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from core.models import UserLocation
from .models import UserRole
from .utils import generate_initial_pin

User = get_user_model()

class LoginSerializer(serializers.Serializer):
      phone = serializers.CharField()
      pin = serializers.CharField(write_only=True)

      default_error_messages = {
            "invalid_credentials": "Invalid phone number or pin.",
      }

      def validate_phone(self, value):
        try:
            parsed = phonenumbers.parse(value, "CA")
        except phonenumbers.NumberParseException:
            self.fail("invalid_credentials")

        if not phonenumbers.is_valid_number(parsed):
            self.fail("invalid_credentials")

        return phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.E164
        )

      def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["phone"],
            password=attrs["pin"],
        )

        if user is None:
            self.fail("invalid_credentials")

        attrs["user"] = user
        return attrs

class ChangePinSerializer(serializers.Serializer):
    current_pin = serializers.CharField(write_only=True)
    new_pin = serializers.CharField(write_only=True)

    WEAK_PINS = {"000000", "111111", "123456", "654321", "121212"}

    def validate_current_pin(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current PIN is incorrect.")
        return value

    def validate_new_pin(self, value):
        if len(value) != 6:
            raise serializers.ValidationError("PIN must be exactly 6 digits.")
        if not value.isdigit():
            raise serializers.ValidationError("PIN must contain only numbers.")
        if value in self.WEAK_PINS:
            raise serializers.ValidationError("That PIN is too easy to guess.")
        if len(set(value)) == 1:
            raise serializers.ValidationError("PIN cannot be all the same digit.")

        user = self.context["request"].user
        if str(user.phone).endswith(value[-4:]):
            raise serializers.ValidationError(
                "PIN cannot contain the last 4 digits of your phone number."
            )
        return value

    def validate(self, attrs):
        if attrs["current_pin"] == attrs["new_pin"]:
            raise serializers.ValidationError(
                {"new_pin": "New PIN must be different from your current PIN."}
            )
        return attrs

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_pin"])
        user.must_change_pin = False
        user.save(update_fields=["password", "must_change_pin"])
        return user

class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField()
    locations = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "phone",
            "first_name",
            "last_name",
            "role",
            "must_change_pin",
            "locations",
        )

    def get_locations(self, obj):
        return [
            {
                "id": link.location_id,
                "name": link.location.name,
                "is_primary": link.is_primary,
            }
            for link in obj.location_links.select_related("location")
        ]

class UserCreateSerializer(serializers.ModelSerializer):
    phone = serializers.CharField()
    initial_pin = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "phone",
            "first_name",
            "last_name",
            "initial_pin",
            "role",
        )

    def validate_phone(self, value):
        try:
            parsed = phonenumbers.parse(value, "CA")
        except phonenumbers.NumberParseException:
            raise serializers.ValidationError("Enter a valid phone number.")

        if not phonenumbers.is_valid_number(parsed):
            raise serializers.ValidationError("Enter a valid phone number.")

        normalized = phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.E164
        )

        if User.objects.filter(phone=normalized).exists():
            raise serializers.ValidationError(
                "A user with that phone number already exists."
            )
        return normalized

    def validate_role(self, value):
        creator = self.context["request"].user

        if creator.role == UserRole.ADMIN:
            return value

        if value in (UserRole.MANAGER, UserRole.ADMIN):
            raise serializers.ValidationError(
                "You cannot create a user with that role."
            )
        return value

    def create(self, validated_data):
        creator = self.context["request"].user

        link = creator.location_links.filter(is_primary=True).first()
        if link is None:
            raise serializers.ValidationError(
                "You are not assigned to a location."
            )

        pin = generate_initial_pin(
            validated_data.get("first_name", ""),
            validated_data.get("last_name", ""),
            validated_data["phone"],
        )

        user = User.objects.create_user(
            phone=validated_data["phone"],
            password=pin,
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            role=validated_data["role"],
            must_change_pin=True,
        )

        UserLocation.objects.create(
            user=user, location=link.location, is_primary=True
        )

        user.initial_pin = pin
        return user