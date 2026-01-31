from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from delivery.models import Delivery
from delivery.serializers.delivery import DeliverySerializer
from notification.services import NotificationService
from utils.user_role_based_permissions import AdminUserPermission


class UpdateDeliveryStatus(APIView):
    """
    API view to update delivery status.
    Validates state transitions and sends notifications.
    """
    serializer_class = DeliverySerializer
    # permission_classes = [AdminUserPermission]
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_id="update_delivery_status",
        operation_description=(
                "Update delivery status following state machine rules:\n\n"
                "Valid transitions:\n"
                "- CREATED → ASSIGNED\n"
                "- ASSIGNED → IN_TRANSIT\n"
                "- IN_TRANSIT → COMPLETED or FAILED\n\n"
                "Terminal states (COMPLETED, FAILED) cannot be updated."
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["status"],
            properties={
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="New delivery status",
                    enum=['ASSIGNED', 'IN_TRANSIT', 'COMPLETED', 'FAILED'],
                    example='IN_TRANSIT'
                ),
            }
        ),
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="Delivery status updated successfully"
                    ),
                    "data": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                            "status": openapi.Schema(type=openapi.TYPE_STRING, example="IN_TRANSIT"),
                            "product_name": openapi.Schema(type=openapi.TYPE_STRING, example="Laptop"),
                        }
                    ),
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="Invalid transition from CREATED to COMPLETED"
                    )
                }
            ),
            status.HTTP_404_NOT_FOUND: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="Delivery not found"
                    )
                }
            ),
        },
        tags=["Delivery"]
    )
    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        new_status = request.data.get('status')

        if not new_status:
            return Response({"message": "status field is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Lock the row for update
            delivery = Delivery.objects.select_for_update().get(pk=pk)
        except Delivery.DoesNotExist:
            return Response({"message": "Delivery not found"}, status=status.HTTP_404_NOT_FOUND)

        old_status = delivery.status

        # Check if delivery is in terminal state
        if old_status in Delivery.TERMINAL_STATES:
            return Response({"message": f"Cannot update delivery in {delivery.status} state. This is a terminal state."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate status transition
        can_transition, message = delivery.can_transition_to(new_status)
        if not can_transition:
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)

        # Update status
        serializer = self.serializer_class(delivery, data={'status': new_status}, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()

            # Send notification to the user who created the delivery
            NotificationService.notify_status_changed(
                delivery=delivery,
                old_status=old_status,
                new_status=new_status,
            )

            return Response({"message": "Delivery status updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)