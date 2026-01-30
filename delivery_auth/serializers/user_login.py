from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import update_last_login
from rest_framework import serializers


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for handling user login by validating email and password credentials.

    This serializer accepts an email and password, verifies them against the user model,
    authenticates the user, and updates the last login timestamp upon successful validation.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validates the provided email and password to authenticate a user.

        This method checks if the email exists in the database, verifies the password,
        and authenticates the user using Django's authentication system. If successful,
        it updates the user's last login timestamp and adds the authenticated user to
        the data dictionary.

        Args:
            data (dict): A dictionary containing 'email' and 'password' keys.

        Returns:
            dict: The input data dictionary with an additional 'user' key containing
                  the authenticated user object.

        Raises:
            serializers.ValidationError: If the email is incorrect, the password is
                                        incorrect, or the user is not valid.
        """
        email = data.get("email")
        password = data.get("password")

        user = get_user_model().objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError(detail={"email": "Incorrect Email !!"})
        verify_pass = user.check_password(password)
        if not verify_pass:
            raise serializers.ValidationError(detail={"password": "Incorrect Password !!"})

        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("You are not valid User !! ")

        data["user"] = user

        update_last_login(None, user)

        return data
