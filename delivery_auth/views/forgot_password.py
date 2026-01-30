import os

from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from delivery_auth.models import AuthUser
from utils.tasks import send_mail_func
from delivery_auth.serializers.forgot_password import ForgotPasswordSerializer

FRONTEND_URL = os.environ.get('FRONTEND_URL')


class ForgotPasswordView(APIView):
    """
        API view to handle password reset requests by sending a reset link to the user's email.

        This view processes POST requests containing the user's email, verifies the user's existence,
        generates a password reset token, and sends an email with a reset link.

        Attributes:
            serializer_class (Serializer): The serializer class for validating input data.

        Methods:
            post(request, *args, **kwargs): Handles the POST request to initiate password reset.
    """
    # serializer_class = ForgotPasswordSerializer

    @swagger_auto_schema(
        operation_id="forgot_password",
        operation_description="Request password reset by sending reset link to user's email",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email"],
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="Valid email address of the user requesting password reset",
                    example="john.doe@example.com"
                ),
            }
        ),
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Success message indicating reset email was sent",
                        example="Password reset email sent successfully"
                    ),
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Error message for invalid request",
                        example="User with this email does not exist"
                    ),
                    "field_errors": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description="Field-specific validation errors",
                        example={
                            "email": ["Please enter a valid email address."]
                        }
                    ),
                }
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Internal server error message",
                        example="Failed to send password reset email"
                    ),
                }
            ),
        },
        tags=["Auth"]
    )
    def post(self, request, *args, **kwargs):
        """
        Handle POST request to send a password reset email with template.

        Args:
            request (Request): The HTTP request object containing the user's email.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: HTTP response with success or failure message.
                - 200: Success response if email is sent.
                - 400: Bad request if user is not found.
        """
        email = request.data.get("email")
        user = AuthUser.objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(reverse("forgot-password-confirm", args=[user.id, token]))
            context = {
                'user': user,
                'user_id': user.id,
                'token': token,
                'reset_link': reset_link,
                'site_name': 'Delivery Aggregator Platform',
                'protocol': 'https' if request.is_secure() else 'http',
                'domain': request.get_host(),
            }
            html_message = render_to_string('emails/forgot_password.html', context)
            plain_message = strip_tags(html_message)
            send_mail_func.delay(
                subject="Reset Your Password",
                html_message=html_message,
                plain_message=plain_message,
                from_email="ajay.softechpark@gmail.com",
                recipient_list=[email]
            )
            return Response({"message": "Password reset email sent successfully"}, status=status.HTTP_200_OK)
        return Response(
            {"message": "User with this email does not exist"}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordConfirmView(generics.UpdateAPIView):
    """
        API view to handle password reset confirmation and update.

        This view processes PUT requests to validate the password reset token and update
        the user's password if the token is valid and the new passwords match.

        Attributes:
            serializer_class (Serializer): The serializer class for validating password data.

        Methods:
            update(request, *args, **kwargs): Handles the PUT request to update the password.
    """
    serializer_class = ForgotPasswordSerializer

    @swagger_auto_schema(
        operation_id="forgot_password_confirm",
        operation_description="Confirm password reset with token and set new password",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["new_password", "confirm_new_password"],
            properties={
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description="New password (8-16 characters, must contain uppercase letter and special character)",
                    minLength=8,
                    maxLength=16,
                    example="MyNewPassword123!"
                ),
                "confirm_new_password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description="Confirmation of new password (must match new_password)",
                    minLength=8,
                    maxLength=16,
                    example="MyNewPassword123!"
                ),
            }
        ),
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Success message confirming password change",
                        example="Password changed successfully"
                    ),
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Error message for invalid request",
                        example="New password and confirm password do not match"
                    ),
                    "field_errors": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description="Field-specific validation errors",
                        example={
                            "new_password": ["Password must contain at least one uppercase letter."],
                            "confirm_new_password": ["This field is required."]
                        }
                    ),
                }
            ),
            status.HTTP_404_NOT_FOUND: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Error message when user is not found",
                        example="User not found"
                    ),
                }
            ),
            status.HTTP_401_UNAUTHORIZED: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Error message when token is invalid or expired",
                        example="Invalid or expired password reset token"
                    ),
                }
            ),
        },
        tags=["Auth"]
    )
    def update(self, request, *args, **kwargs):
        """
            Handle PUT request to confirm and update the user's password.

            Args:
                request (Request): The HTTP request object containing new password data.
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments including user_id and token.

            Returns:
                Response: HTTP response with success or failure message.
                    - 200: Success response if password is updated.
                    - 400: Bad request if token is invalid or passwords don't match.
        """
        user_id = kwargs.get("user_id")
        token = kwargs.get("token")

        user = get_object_or_404(AuthUser, id=user_id)

        if default_token_generator.check_token(user, token):
            # Token is valid, allow the user to set a new password
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # old_password = serializer.validated_data.get("old_password")
            new_password = serializer.validated_data["new_password"]
            confirm_new_password = serializer.validated_data["confirm_new_password"]

            # Check the old password if provided
            # if old_password and not user.check_password(old_password):
            #     return Response(
            #         {"message": "Invalid old password."},
            #         status=status.HTTP_400_BAD_REQUEST,
            #     )

            if new_password != confirm_new_password:
                return Response({"message": "New password and confirm password do not match..."}, status=status.HTTP_400_BAD_REQUEST, )
                # Set the new password
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password updated..."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Something went wrong while password reset..."}, status=status.HTTP_400_BAD_REQUEST)
