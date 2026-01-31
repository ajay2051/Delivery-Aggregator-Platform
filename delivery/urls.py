from django.urls import path

from delivery.views.deliveries_list import ListDeliveries
from delivery.views.request_deliveries import RequestDeliveries

urlpatterns = [
    path('request/', RequestDeliveries.as_view(), name='request_deliveries'),
    path('list/', ListDeliveries.as_view(), name='list_deliveries'),
]