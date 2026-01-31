from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from delivery.models import Delivery
from delivery.serializers.delivery import DeliverySerializer
from delivery_auth.models import AuthUser
from notification.services import NotificationService
from utils.user_role_based_permissions import SuperAdminPermission


class AssignDeliveries(APIView):
    """
    API view to assign a delivery to an admin user.

    Only super admins can assign deliveries to admin users.
    """
    serializer_class = DeliverySerializer
    permission_classes = [permissions.IsAuthenticated]
    # permission_classes = [SuperAdminPermission]

    @swagger_auto_schema(
        operation_id="assign_delivery",
        operation_description="Assign a delivery to an admin user. Only super admins can perform this action.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["assigned_to"],
            properties={
                "assigned_to": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the admin user to assign the delivery to",
                    example=5
                ),
            }
        ),
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="Delivery assigned to admin successfully"
                    ),
                    "data": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                            "assigned_to": openapi.Schema(type=openapi.TYPE_INTEGER, example=5),
                            "status": openapi.Schema(type=openapi.TYPE_STRING, example="assigned"),
                        }
                    ),
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="assigned_to field is required"
                    )
                }
            ),
            status.HTTP_403_FORBIDDEN: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="User is not an admin"
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
    def patch(self, request, pk, *args, **kwargs):
        assigned_to_id = request.data.get('assigned_to')

        if not assigned_to_id:
            return Response({"message": "assigned_to field is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            delivery = Delivery.objects.get(pk=pk)
        except Delivery.DoesNotExist:
            return Response({"message": "Delivery not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            auth_user = AuthUser.objects.get(id=assigned_to_id)
        except AuthUser.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if auth_user.role != 'admin':
            return Response({"message": "User is not an admin"}, status=status.HTTP_403_FORBIDDEN)

        update_data = {
            'assigned_to': assigned_to_id,
            'status': 'ASSIGNED'
        }

        serializer = self.serializer_class(delivery, data=update_data, partial=True, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            NotificationService.create_delivery_notification(
                delivery=delivery,
                notification_type='delivery_assigned',
                title='Delivery Assigned',
                message=f"Your delivery for {delivery.product_name} has been assigned to {delivery.assigned_to.first_name} {delivery.assigned_to.last_name}")
            return Response({"message": "Delivery assigned to admin successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
