from celery import shared_task
from django.core.mail import EmailMultiAlternatives


@shared_task
def send_mail_func(subject, html_message, plain_message, from_email, recipient_list):
    """
    Send email with both HTML and plain text versions
    """
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=from_email,
            to=recipient_list
        )
        msg.attach_alternative(html_message, "text/html")
        msg.send()
        return "Email sent successfully...🤣🤣"
    except ValueError as e:
        return f"Failed to send email: {str(e)}"