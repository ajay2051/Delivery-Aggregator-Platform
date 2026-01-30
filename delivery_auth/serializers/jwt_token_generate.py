from typing import Dict

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenVerifySerializer


class DefaultTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
        Custom serializer for getting JWT token pairs, extending the default
        `TokenObtainPairSerializer` to include additional user information in the token.

        This serializer adds user-specific fields (full_name, email, role, and user_id)
        to the JWT token payload if those attributes exist on the user object.
    """
    @classmethod
    def user_get_token(cls, user):
        """
            Generates a JWT token for the given user, including additional user attributes.

            Args:
                user: The user instance for which the token is generated.

            Returns:
                Token: A JWT token with additional user fields (full_name, email, role, user_id)
                       included in the payload if they exist on the user object.
        """
        token = super().get_token(user)
        if hasattr(user, "first_name"):
            token["first_name"] = user.first_name
        if hasattr(user, "last_name"):
            token["last_name"] = user.last_name
        if hasattr(user, "email"):
            token["email"] = user.email
        if hasattr(user, "user_number"):
            token["user_number"] = user.user_number
        if hasattr(user, "role"):
            token["role"] = user.role
        if hasattr(user, "country"):
            token["country"] = user.country
        if hasattr(user, "date_of_birth"):
            token["date_of_birth"] = user.date_of_birth.isoformat() if user.date_of_birth else "No Date Of Birth"
        if hasattr(user, "id"):
            token["user_id"] = user.id

        return token


class DefaultTokenVerificationSerializer(TokenVerifySerializer):
    """
        Custom serializer for verifying JWT tokens, extending the default
        `TokenVerifySerializer` to simplify the validation response.

        This serializer returns a boolean indicating whether the token is valid,
        simplifying the response compared to the default implementation.
    """
    def validate(self, attrs: Dict[str, None]) -> bool:
        """
            Validates the provided JWT token attributes.

            Args:
                attrs (Dict[str, None]): A dictionary containing the token to be verified.

            Returns:
                bool: True if the token is valid (empty response from parent validator),
                      False otherwise.
        """
        data = super().validate(attrs)
        if data == {}:
            return True
        else:
            return False
