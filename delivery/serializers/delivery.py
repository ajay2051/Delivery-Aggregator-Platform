from rest_framework import serializers

from delivery.models import Delivery


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = [
            'id',
            'product_name',
            'status',
            'delivery_date',
            'delivery_address',
            'assigned_to',
            'created_by',
            'created_at',
            'updated_at'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_by_full_name'] = instance.created_by.first_name + ' ' + instance.created_by.last_name
        return data
