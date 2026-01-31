from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from delivery_auth.models import AuthUser


@api_view(['GET'])
@swagger_auto_schema(
        operation_id='verify_users',
        operation_description="Verify Users",
        tags=["Auth"]
    )
def verify_user_account(request, user_id, token):
    # Don't remove token
    try:
        if request.method == "GET":
            user = AuthUser.objects.filter(id=user_id).first()
            if not user:
                raise ValidationError("User not found...")
            if user.is_verified:
                raise ValidationError("User is already verified...")
            user.is_verified = True
            user.save()
        return redirect(f"http://127.0.0.1:8000/verified")
    except ValidationError:
        return Response("Something went wrong...👿👿", status=status.HTTP_400_BAD_REQUEST)
