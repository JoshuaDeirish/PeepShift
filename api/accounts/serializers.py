from rest_framework import serializers
import phonenumbers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

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