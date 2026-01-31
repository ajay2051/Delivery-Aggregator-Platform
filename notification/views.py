from django.http import StreamingHttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
import json
import time

from notification.models import Notification
from utils.user_role_based_permissions import PartnerUserPermission


@swagger_auto_schema(
    method='get',
    operation_id="notification_stream",
    operation_description=(
            "Stream unread notifications to the authenticated partner user using "
            "Server-Sent Events (SSE). The client can optionally provide `last_id` "
            "to receive notifications created after that ID."
    ),
    manual_parameters=[
        openapi.Parameter(
            name="last_id",
            in_=openapi.IN_QUERY,
            description="Last received notification ID (used to fetch newer notifications)",
            type=openapi.TYPE_INTEGER,
            required=False,
            example=10,
        ),
    ],
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=12),
                "title": openapi.Schema(type=openapi.TYPE_STRING, example="New Order"),
                "message": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="You have a new delivery request",
                ),
                "type": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="delivery",
                ),
                "created_at": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format="date-time",
                    example="2026-01-31T10:45:30Z",
                ),
            },
            description="Each SSE event emits a single notification object",
        ),
        401: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="Authentication credentials were not provided",
                )
            },
        ),
        403: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="You do not have permission to perform this action",
                )
            },
        ),
    },
    tags=["Notifications"],
)
@api_view(['GET'])
@permission_classes([PartnerUserPermission])
def notification_stream(request):
    """Stream notifications to client using SSE."""

    def event_stream():
        # Convert last_id to integer
        last_id = int(request.GET.get('last_id', 0))

        # Send initial connection confirmation (heartbeat)
        yield f": connected\n\n"

        try:
            while True:
                # Check for new notifications
                notifications = Notification.objects.filter(recipient=request.user, id__gt=last_id, is_read=False).order_by('id')

                for notification in notifications:
                    data = {
                        'id': notification.id,
                        'title': notification.title,
                        'message': notification.message,
                        'type': notification.notification_type,
                        'created_at': notification.created_at.isoformat(),
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                    last_id = notification.id

                # Send heartbeat to keep connection alive
                yield f": heartbeat\n\n"

                time.sleep(2)  # Poll every 2 seconds

        except GeneratorExit:
            # Client disconnected
            pass

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response