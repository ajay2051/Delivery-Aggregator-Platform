from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from delivery_auth.models import AuthUser
from delivery_auth.serializers.create_users import AuthUserSerializers
from utils.pagination import CustomPagination


class UsersListAPIView(APIView):
    """
    API view for listing all users with filtering, sorting, and pagination.

    This view retrieves a list of users based on provided query parameters
    such as full name, email, role, and search terms. It supports sorting
    by creation date or alphabetically and uses custom pagination for
    efficient data retrieval.

    Attributes:
        serializer_class (AuthUserSerializers): Serializer for user data.
        permission_classes (list): Requires authenticated access.
        pagination_class (CustomPagination): Custom pagination for query results.
    """
    # queryset = TestPaper.objects.filter(is_deleted=False).order_by('-id')
    serializer_class = AuthUserSerializers
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    @swagger_auto_schema(
        operation_id='list_users',
        operation_description="List All Users",
        responses={200: AuthUserSerializers, 400: 'Bad Request'},
        tags=["Auth"]
    )
    def get_queryset(self):
        """
            Retrieve the base queryset of users.

            Filters out deleted users and orders them by ID in descending order.

            Args:
                request (Request): The HTTP request object.

            Returns:
                QuerySet: A queryset of AuthUser objects that are not deleted.
        """
        return AuthUser.objects.filter(is_deleted=False).order_by('-id')

    def get(self, request, *args, **kwargs):
        """
            Handle GET requests to list users.

            Supports filtering by full name, email, role, and a general search term.
            Allows sorting by latest, oldest, or alphabetical order. Results are
            paginated using the custom pagination class.

            Args:
                request (Request): The HTTP request object containing query parameters.
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Query Parameters:
                first_name (str, optional): Filter by user's first name.
                last_name (str, optional): Filter by user's last name.
                email (str, optional): Filter by user's email.
                role (str, optional): Filter by user's role.
                search (str, optional): Search across full name, email, and role.
                sort_by (str, optional): Sort results by 'latest', 'oldest', or 'alphabet'.

            Returns:
                Response: A Response object containing:
                    - message: Success message.
                    - data: Serialized list of user data (paginated or full).
                    - Pagination metadata if pagination is applied.

            Status Codes:
                200: Successfully retrieved user list.
                400: Bad request if query parameters are invalid.
        """
        paginator = self.pagination_class()
        first_name = self.request.query_params.get('first_name', None)
        last_name = self.request.query_params.get('last_name', None)
        email = self.request.query_params.get('email', None)
        role = self.request.query_params.get('role', None)
        sort_by = self.request.query_params.get("sort_by", None)
        phone_number = self.request.query_params.get("phone_number", None)
        country = self.request.query_params.get("country", None)
        search = self.request.query_params.get('search', None)
        query = Q()
        if first_name:
            query &= Q(first_name__icontains=first_name)
        if last_name:
            query &= Q(last_name__icontains=last_name)
        if email:
            query &= Q(email__icontains=email)
        if role:
            query &= Q(role__icontains=role)
        if phone_number:
            query &= Q(user_number__icontains=phone_number)
        if country:
            query &= Q(country__icontains=country)
        if search:
            query &= (
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search) |
                    Q(email__icontains=search) |
                    Q(role__icontains=search) |
                    Q(user_number__icontains=search) |
                    Q(country__icontains=search)
            )
        queryset = self.get_queryset().filter(query)
        if sort_by == 'latest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort_by == 'alphabet':
            queryset = queryset.order_by('first_name')
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response({"message": "User Successfully Listed", "data": serializer.data}, status=status.HTTP_200_OK)


class UserDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='delete_users',
        operation_description="Delete Single Users",
        responses={200: "Deleted Success", 400: 'Bad Request'},
        tags=["Auth"]
    )
    def delete(self, request, pk):
        try:
            users = AuthUser.objects.get(id=pk)
        except AuthUser.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        users.delete()
        return Response({"message": "Users Deleted Successfully..."}, status=status.HTTP_204_NO_CONTENT)
