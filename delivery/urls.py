from django.urls import path

from delivery.views.assign_deliveries import AssignDeliveries
from delivery.views.deliveries_list import ListDeliveries
from delivery.views.request_deliveries import RequestDeliveries

urlpatterns = [
    path('request/', RequestDeliveries.as_view(), name='request_deliveries'),
    path('list/', ListDeliveries.as_view(), name='list_deliveries'),
    path('assign/<int:pk>/', AssignDeliveries.as_view(), name='assign_deliveries'),
]