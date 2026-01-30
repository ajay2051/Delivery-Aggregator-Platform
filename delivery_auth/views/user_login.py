import jwt
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from delivery_auth.serializers.jwt_token_generate import DefaultTokenObtainPairSerializer
from delivery_auth.serializers.user_login import UserLoginSerializer


class UserLoginView(APIView):
    """
    API view for handling user login functionality.

    This view processes user login requests, validates credentials,
    generates JWT tokens, and returns user information along with
    authentication tokens.

    Attributes:
        serializer_class (UserLoginSerializer): The serializer class for validating login data.
        permission_classes (list): List of permission classes, set to AllowAny to permit unauthenticated access.
    """

    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_id="user_login",
        operation_description="User Login",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Email Address"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Password"
                ),
            },
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(type=openapi.TYPE_STRING, example="Successfully Logged In"),
                    "access": openapi.Schema(type=openapi.TYPE_STRING, example="your_access_token"),
                    "refresh": openapi.Schema(type=openapi.TYPE_STRING, example="your_refresh_token"),
                    "data": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "email": openapi.Schema(type=openapi.TYPE_STRING, example="helloo@gmail.com")
                        },
                    ),
                    "user": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "email": openapi.Schema(type=openapi.TYPE_STRING, example="helloo@gmail.com"),
                            "full_name": openapi.Schema(type=openapi.TYPE_STRING, example="ajay thakur"),
                            "role": openapi.Schema(type=openapi.TYPE_STRING, example="student"),
                            "user_number": openapi.Schema(type=openapi.TYPE_STRING, example="user_number"),
                            "user_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=2),
                            "last_login": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, example="2025-05-23T04:18:51.142868Z"),
                        },
                    ),
                },
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "status": openapi.Schema(type=openapi.TYPE_NUMBER, example=401),
                    "message": openapi.Schema(type=openapi.TYPE_STRING, example="Invalid credentials"),
                },
            ),
        },
        tags=["Auth"]
    )
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for user login.

        Validates user credentials, generates access and refresh tokens,
        decodes the access token to extract user information, and returns
        a response containing the tokens and user details.

        Args:
            request (Request): The HTTP request object containing login data (email, password).
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A Response object containing:
                - message: Success message.
                - access: Access token as a string.
                - refresh: Refresh token as a string.
                - data: Serialized login data.
                - user: Dictionary containing user details (email, full_name, role, user_id, last_login).

        Raises:
            ValidationError: If the provided login data is invalid.
        """

        perm = None
        sub_perm = None
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get("user", None)
        if not user.is_verified:
            raise ValidationError("User is not verified...")
        refresh_token = DefaultTokenObtainPairSerializer.user_get_token(user=user)
        access_token = refresh_token.access_token

        access_token_string = str(access_token)

        access_token_bytes = access_token_string.encode("utf-8")

        # Decode access token to get user_type
        decoded_token = jwt.decode(
            access_token_bytes,
            options={"verify_signature": False},
            algorithms=["HS256"],
        )
        email = decoded_token.get("email", None)
        role = decoded_token.get("role", None)
        user_id = decoded_token.get("user_id", None)
        first_name = decoded_token.get("first_name", None)
        last_name = decoded_token.get("last_name", None)
        study_level = decoded_token.get("study_level", None)
        country = decoded_token.get("country", None)
        user_number = decoded_token.get("user_number", None)
        date_of_birth = decoded_token.get("date_of_birth", None)

        # access_exp, refresh_exp = self.user_type_access_refresh_token(user=user)
        #
        # refresh_token.set_exp(
        #     claim="exp", lifetime=datetime.timedelta(minutes=int(refresh_exp))
        # )
        # access_token.set_exp(
        #     claim="exp", lifetime=datetime.timedelta(minutes=int(access_exp))
        # )

        response = Response(
            {
                "message": "Successfully Logged In...🙂🙂",
                "access": str(refresh_token.access_token),
                "refresh": str(refresh_token),
                "data": serializer.data,
                "user": {
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": role,
                    "user_number": user_number,
                    "country": country,
                    "date_of_birth": date_of_birth,
                    "user_id": user_id,
                    "last_login": user.last_login,
                    "timezone": str(settings.TIME_ZONE),
                }

            },
            status=status.HTTP_200_OK,
        )
        # response.set_cookie(key=str("access_token"), value=str(access_token), domain="192.168.101.129:8000", secure=True)
        # response.set_cookie(key=str("refresh_token"), value=str(refresh_token), domain="192.168.101.129:8000", secure=True)
        # response.set_cookie(key=str("ai_token"), value=str(ai_token_dict), domain="192.168.101.129:8000", secure=True)
        return response
