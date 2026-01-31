from django.urls import path

from notification.views import notification_stream

urlpatterns = [
    path('stream/', notification_stream, name='notification-stream'),
]