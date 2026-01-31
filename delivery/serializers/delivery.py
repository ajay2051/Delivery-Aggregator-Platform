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

    def validate_status(self, value):
        """Validate status transitions."""
        instance = self.instance

        # If creating new delivery, only CREATED is allowed
        if not instance:
            if value != 'CREATED':
                raise serializers.ValidationError("New deliveries must have status 'CREATED'")
            return value

        # If updating, validate transition
        if instance.status != value:
            can_transition, message = instance.can_transition_to(value)
            if not can_transition:
                raise serializers.ValidationError(message)
        return value

    def validate(self, attrs):
        """Additional validation logic."""
        instance = self.instance

        # If status is being changed to ASSIGNED, assigned_to must be set
        if 'status' in attrs and attrs['status'] == 'ASSIGNED':
            assigned_to = attrs.get('assigned_to') or (instance.assigned_to if instance else None)
            if not assigned_to:
                raise serializers.ValidationError({'assigned_to': 'assigned_to is required when status is ASSIGNED'})
        return attrs
