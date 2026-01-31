from django.urls import path

from delivery_auth.views.create_users import CreateUserView
from delivery_auth.views.forgot_password import ForgotPasswordView
from delivery_auth.views.user_login import UserLoginView
from delivery_auth.views.users_lists import UsersListAPIView, UserDeleteAPIView
from delivery_auth.views.verify_users import verify_user_account

urlpatterns = [
    path('create_user/', CreateUserView.as_view(), name='create_user'),
    path('login/', UserLoginView.as_view(), name='login'),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path('list_users/', UsersListAPIView.as_view(), name='list_users'),
    path('verify_users/<int:user_id>/<str:token>/', verify_user_account, name='verify_users'),
    path('delete_users/<int:pk>/', UserDeleteAPIView.as_view(), name='delete_users'),

]