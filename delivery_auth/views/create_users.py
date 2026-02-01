from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from delivery_auth.models import AuthUser
from delivery_auth.serializers.create_users import AuthUserSerializers
from delivery_auth.celery_tasks import send_mail_func


class CreateUserView(generics.CreateAPIView):
    """
        API view to create a new user.

        This view handles the creation of a new user by accepting user data,
        validating it, and saving it to the database. It allows any user
        (authenticated or not) to access this endpoint.

        Attributes:
            queryset: Queryset of all AuthUser objects.
            serializer_class: Serializer class for validating and serializing user data.
            permission_classes: Permissions allowing any user to access this view.
    """
    queryset = AuthUser.objects.all()
    serializer_class = AuthUserSerializers
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_id='create_user',
        operation_description='Create a new user account with validation',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["full_name", "email", "password", "date_of_birth"],
            properties={
                "first_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="First name (max 20 characters, letters only)",
                    maxLength=20,
                    example="John Doe",
                    pattern="^[a-zA-Z\\s]+$"
                ),
                "last_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Last name (max 20 characters, letters only)",
                    maxLength=20,
                    example="John Doe",
                    pattern="^[a-zA-Z\\s]+$"
                ),
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="Valid email address (max 50 characters)",
                    maxLength=50,
                    example="john.doe@example.com"
                ),
                "user_number": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="User Phone number",
                    maxLength=20,
                    example="+9779852314785"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_PASSWORD,
                    description="Password (8-16 characters, must contain uppercase letter and special character)",
                    minLength=8,
                    maxLength=16,
                    example="MyPassword123!"
                ),
                "country": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Country of origin (max 30 characters)",
                    maxLength=30,
                    example="United States"
                ),
                "date_of_birth": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATE,
                    description="Date of birth (must be 16+ years old, format: YYYY-MM-DD)",
                    example="1990-01-15"
                ),
                "role": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="User role",
                    example="student"
                ),
                "is_superuser": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="User role",
                    example="true"
                ),
                "extras": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description="Additional user metadata (JSON object)",
                    example={"preferences": {"notifications": True}}
                ),
            }
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="New user created successfully"
                    ),
                    "data": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="Unique user identifier",
                                example=1
                            ),
                            "full_name": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="John Doe"
                            ),
                            "email": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                format=openapi.FORMAT_EMAIL,
                                example="john.doe@example.com"
                            ),
                            "country": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="United States"
                            ),
                            "date_of_birth": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                format=openapi.FORMAT_DATE,
                                example="1990-01-15"
                            ),

                            "role": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                example="student"
                            ),


                            "is_superuser": openapi.Schema(
                                type=openapi.TYPE_BOOLEAN,
                                description="Whether the user is a superuser",
                                example=False
                            ),
                            "created_at": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                format=openapi.FORMAT_DATETIME,
                                description="User creation timestamp",
                                example="2024-01-15T10:30:00Z"
                            ),
                            "updated_at": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                format=openapi.FORMAT_DATETIME,
                                description="User last update timestamp",
                                example="2024-01-15T10:30:00Z"
                            ),

                            "extras": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                description="Additional user metadata",
                                example={"preferences": {"notifications": True}}
                            ),

                        }
                    ),
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "field_errors": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description="Field-specific validation errors",
                        example={
                            "full_name": ["Full name must be at most 20 characters long."],
                            "password": ["Password must contain at least one uppercase letter."],
                            "email": ["Please enter a valid email address."],
                            "date_of_birth": ["You must be at least 16 years old."]
                        }
                    ),
                    "non_field_errors": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING),
                        description="General validation errors",
                        example=["This field is required."]
                    ),
                }
            ),
            status.HTTP_409_CONFLICT: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Conflict error message",
                        example="User with this email already exists."
                    ),
                }
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Internal server error message",
                        example="An unexpected error occurred while creating the user."
                    ),
                }
            ),
        },
        tags=["Auth"]
    )
    def create(self, request, *args, **kwargs):
        """
            Create a new user with the provided data.

            Args:
                request: The HTTP request containing user data in JSON format.
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                Response: A response object containing a success message and the
                          serialized user data with HTTP 200 status.

            Raises:
                serializers.ValidationError: If the provided data is invalid.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        email = request.data.get("email")
        user = AuthUser.objects.filter(email=email).first()
        try:
            if user:
                token = default_token_generator.make_token(user)
                verification_link = request.build_absolute_uri(reverse("verify_users", args=[user.id, token]))
                context = {
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'verification_link': verification_link,
                    'site_name': 'Delivery Aggregator Platform',
                    'protocol': 'https' if request.is_secure() else 'http',
                    'domain': request.get_host(),
                }
                html_message = render_to_string('emails/user_verification.html', context)
                plain_message = strip_tags(html_message)
                send_mail_func.delay(
                    subject="Activate your Delivery Aggregator Platform Account",
                    html_message=html_message,
                    plain_message=plain_message,
                    from_email="ajay.softechpark@gmail.com",
                    recipient_list=[email]
                )

            return Response({"message": "Register Success. Please Check Email For Verification...", "data": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": "Some error occurred while creating user", "data": str(e)}, status=status.HTTP_400_BAD_REQUEST)
