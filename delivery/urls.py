from django.urls import path

from delivery.views.request_deliveries import RequestDeliveries

urlpatterns = [
    path('request/', RequestDeliveries.as_view(), name='request_deliveries'),
]