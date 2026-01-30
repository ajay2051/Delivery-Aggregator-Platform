import re

from rest_framework import serializers


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for forgot password functionality.

    Fields:
        email: Required for initiating password reset
        new_password: Required for password confirmation
        confirm_new_password: Required for password confirmation
    """
    # email = serializers.EmailField(
    #     required=False,
    #     help_text="Valid email address for password reset request"
    # )
    new_password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
        max_length=16,
        help_text="New password (8-16 characters, must contain uppercase letter and special character)"
    )
    confirm_new_password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
        max_length=16,
        help_text="Confirmation of new password"
    )

    def validate_new_password(self, value):
        """
        Validate that the new password meets security requirements.

        Args:
            value (str): The password to validate

        Returns:
            str: The validated password

        Raises:
            serializers.ValidationError: If password doesn't meet requirements
        """
        if not value:
            return value

        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")

        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def validate(self, attrs):
        """
        Validate that passwords match when both are provided.

        Args:
            attrs (dict): Dictionary of field values

        Returns:
            dict: The validated attributes

        Raises:
            serializers.ValidationError: If passwords don't match
        """
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.get('confirm_new_password')

        # Only validate password matching if both passwords are provided
        if new_password and confirm_new_password:
            if new_password != confirm_new_password:
                raise serializers.ValidationError("New password and confirm password do not match.")
        return attrs
