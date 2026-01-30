import re

from rest_framework import serializers

from delivery_auth.models import AuthUser

special_characters = set('@_!#$%^&*()<>?/\\|}{~:')


class AuthUserSerializers(serializers.ModelSerializer):
    """
        Serializer for the AuthUser model.

        This serializer handles the serialization and deserialization of AuthUser
        objects, including validation and creation of new users. The password field
        is write-only to ensure it is not exposed in responses.

        Attributes:
            password: A write-only field for the user's password.
    """
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    user_number = serializers.CharField(required=True)
    role = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    date_of_birth = serializers.DateField(required=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = AuthUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "user_number",
            "password",
            "country",
            "date_of_birth",
            "role",
            "is_superuser",
            "created_at",
            "updated_at",
            "is_deleted",
            "extras",
        ]

    def create(self, validated_data):
        """
            Create a new AuthUser instance with the validated data.

            Args:
                validated_data (dict): Validated data containing user attributes.

            Returns:
                AuthUser: The newly created user instance.
        """
        user = AuthUser.objects.create_user(**validated_data)
        return user

    def validate_first_name(self, value):
        if len(value) > 20:
            raise serializers.ValidationError("First name must be at most 20 characters long.")

        # Check for special characters
        if any(char in special_characters for char in value):
            raise serializers.ValidationError("First name must contain only letters.")

        return value

    def validate_last_name(self, value):
        if len(value) > 20:
            raise serializers.ValidationError("Last name must be at most 20 characters long.")

        # Check for special characters
        if any(char in special_characters for char in value):
            raise serializers.ValidationError("Last name must contain only letters.")

        return value

    def validate_password(self, value):
        if len(value) < 8 or len(value) > 16:
            raise serializers.ValidationError("Password must be 8 to 16 characters long.")

        # Check for at least one uppercase letter
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")

        # Check for at least one special character
        if not any(char in special_characters for char in value):
            raise serializers.ValidationError("Password must contain at least one special character.")

        return value

    def validate_email(self, value):
        if not value:
            return value

        # Email validation using regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError("Please enter a valid email address.")

        if len(value) > 50:
            raise serializers.ValidationError("Email must be at most 50 characters long.")

        if AuthUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists...")

        return value

    def validate_user_number(self, value):

        if len(value) > 30:
            raise serializers.ValidationError("User number must be at most 30 characters long.")

        if AuthUser.objects.filter(user_number=value).exists():
            raise serializers.ValidationError("User with this number already exists...")

        return value

    def validate_country(self, value):
        if value and len(value) > 30:
            raise serializers.ValidationError("Nationality must be at most 30 characters long.")

        return value
