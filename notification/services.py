from notification.models import Notification


class NotificationService:
    """Service to handle delivery notifications."""

    @staticmethod
    def create_delivery_notification(delivery, notification_type, title, message, metadata=None):
        """Create a notification for the delivery creator."""
        if not delivery.created_by:
            return None

        return Notification.objects.create(
            recipient=delivery.created_by,
            delivery=delivery,
            notification_type=notification_type,
            title=title,
            message=message,
            metadata=metadata or {}
        )

    @staticmethod
    def notify_status_changed(delivery, old_status, new_status):
        """Notify when delivery status changes."""
        status_messages = {
            'IN_TRANSIT': f'Your delivery #{delivery.product_name} is now in transit.',
            'COMPLETED': f'Your delivery #{delivery.product_name} has been completed successfully! 🎉',
            'FAILED': f'Your delivery #{delivery.product_name} has failed. Please contact support.',
        }

        notification_types = {
            'COMPLETED': 'delivery_completed',
            'FAILED': 'delivery_failed',
        }

        return NotificationService.create_delivery_notification(
            delivery=delivery,
            notification_type=notification_types.get(new_status, 'status_changed'),
            title=f'Delivery Status Updated',
            message=status_messages.get(new_status, f'Your delivery status changed to {new_status}'),
            metadata={
                'old_status': old_status,
                'new_status': new_status
            }
        )
