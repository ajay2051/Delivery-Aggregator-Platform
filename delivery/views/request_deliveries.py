from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from delivery.models import Delivery
from delivery.serializers.delivery import DeliverySerializer
from utils.idempotency_key import generate_idempotency_key
from utils.user_role_based_permissions import PartnerUserPermission


class RequestDeliveries(APIView):
    """
        API view to create a new delivery request.

        This endpoint allows a partner user to request a delivery.
        The authenticated user will be automatically set as `created_by`.
    """
    permission_classes = [PartnerUserPermission]
    serializer_class = DeliverySerializer

    @swagger_auto_schema(
        operation_id="request_delivery",
        operation_description="Create a new delivery request by an authorized partner user.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["delivery_date"],
            properties={
                "delivery_date": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATE,
                    description="Scheduled delivery date (YYYY-MM-DD)",
                    example="2026-02-05"
                ),
                "assigned_to": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the delivery personnel (optional)",
                    example=12
                ),
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Initial delivery status",
                    example="pending"
                ),
            }
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="Delivery Request Success..."
                    ),
                    "data": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                            "status": openapi.Schema(type=openapi.TYPE_STRING, example="pending"),
                            "delivery_date": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                format=openapi.FORMAT_DATE,
                                example="2026-02-05"
                            ),
                            "assigned_to": openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                example=12
                            ),
                            "created_by": openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                example=5
                            ),
                            "created_at": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                format=openapi.FORMAT_DATETIME,
                                example="2026-01-31T10:30:00Z"
                            ),
                            "updated_at": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                format=openapi.FORMAT_DATETIME,
                                example="2026-01-31T10:30:00Z"
                            ),
                        }
                    ),
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "errors": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        example={
                            "delivery_date": ["This field is required."]
                        }
                    )
                }
            ),
            status.HTTP_403_FORBIDDEN: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "detail": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="You do not have permission to perform this action."
                    )
                }
            ),
        },
        tags=["Delivery"]
    )
    def post(self, request, *args, **kwargs):
        idempotency_key = generate_idempotency_key(user_id=request.user.id, payload=request.data)

        existing_delivery = Delivery.objects.filter(idempotency_key=idempotency_key).first()

        if existing_delivery:
            return Response({"message": "Duplicate request detected...👿👿", }, status=status.HTTP_409_CONFLICT)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(created_by=request.user, idempotency_key=idempotency_key)
            return Response({"message": "Delivery Request Success...🤗🤗", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
