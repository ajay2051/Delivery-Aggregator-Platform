from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from delivery.models import Delivery
from delivery.serializers.delivery import DeliverySerializer
from utils.pagination import CustomPagination


class ListDeliveries(APIView):
    """
    API view to list deliveries based on user role.

    Admins can view deliveries assigned to them.
    Partners can view deliveries they created.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DeliverySerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Delivery.objects.select_related('assigned_to', 'created_by').all()

    @swagger_auto_schema(
        operation_id="list_deliveries",
        operation_description="Retrieve a list of deliveries based on user role. "
                              "Partners see deliveries assigned to them, "
                              "Admins see deliveries they created.",
        manual_parameters=[
            openapi.Parameter(
                'role',
                openapi.IN_QUERY,
                description="User role filter (required). Use 'partner' to see assigned deliveries or 'admin' to see created deliveries.",
                type=openapi.TYPE_STRING,
                required=True,
                enum=['partner', 'admin'],
                example='partner'
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search term to filter deliveries by product name, status, delivery date, address, or user names.",
                type=openapi.TYPE_STRING,
                required=False,
                example='laptop'
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number for pagination",
                type=openapi.TYPE_INTEGER,
                required=False,
                example=1
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Number of items per page",
                type=openapi.TYPE_INTEGER,
                required=False,
                example=10
            ),
        ],
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "count": openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description="Total number of deliveries",
                        example=25
                    ),
                    "next": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="URL to next page",
                        example="http://api.example.com/deliveries/?page=2"
                    ),
                    "previous": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="URL to previous page",
                        example=None
                    ),
                    "results": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                "idempotency_key": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    example="abc123xyz"
                                ),
                                "product_name": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    example="Laptop Dell XPS 15"
                                ),
                                "status": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    example="pending"
                                ),
                                "delivery_date": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    format=openapi.FORMAT_DATE,
                                    example="2026-02-05"
                                ),
                                "delivery_address": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    example="123 Main St, Kathmandu"
                                ),
                                "assigned_to": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=12),
                                        "first_name": openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            example="John"
                                        ),
                                        "last_name": openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            example="Doe"
                                        ),
                                        "email": openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            example="john@example.com"
                                        ),
                                    }
                                ),
                                "created_by": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=5),
                                        "first_name": openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            example="Jane"
                                        ),
                                        "last_name": openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            example="Smith"
                                        ),
                                        "email": openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                            example="jane@example.com"
                                        ),
                                    }
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
                        )
                    ),
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="Please select a role"
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
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="An error occurred while retrieving deliveries"
                    ),
                    "error": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="Error details here"
                    )
                }
            ),
        },
        tags=["Delivery"]
    )
    def get(self, request):
        role = request.query_params.get('role')
        search = request.query_params.get('search')

        # Validate role parameter
        if not role:
            return Response({"message": "Please select a role"}, status=status.HTTP_400_BAD_REQUEST)

        if role not in ['partner', 'admin']:
            return Response({"message": "Invalid role. Must be 'partner' or 'admin'"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get base queryset
            queryset = self.get_queryset()

            # Filter by role
            if role == 'admin':
                queryset = queryset.filter(assigned_to=request.user)
            elif role == 'partner':
                queryset = queryset.filter(created_by=request.user)

            # Apply search filters
            if search:
                query = Q(product_name__icontains=search) | \
                        Q(status__icontains=search) | \
                        Q(delivery_date__icontains=search) | \
                        Q(delivery_address__icontains=search) | \
                        Q(assigned_to__first_name__icontains=search) | \
                        Q(assigned_to__last_name__icontains=search) | \
                        Q(created_by__first_name__icontains=search) | \
                        Q(created_by__last_name__icontains=search)

                queryset = queryset.filter(query)

            # Order by most recent first
            queryset = queryset.order_by('-created_at')

            # Paginate results
            paginator = self.pagination_class()
            page = paginator.paginate_queryset(queryset, request=request)

            if page is not None:
                serializer = self.serializer_class(page, many=True, context={'request': request})
                return paginator.get_paginated_response(serializer.data)

            # If no pagination
            serializer = self.serializer_class(queryset, many=True, context={'request': request})
            return Response({"message": "Deliveries retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": "An error occurred while retrieving deliveries", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)