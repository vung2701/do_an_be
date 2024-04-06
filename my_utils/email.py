from django.conf import settings
from django.core.mail import send_mail


def send_email(recipient_list=None, subject=None, email_body=None, email_body_html=None):
    from_email = settings.EMAIL_HOST_USER  # Replace with your actual email address
    subject = subject or "[ITV] User Information"
    email_message = email_body or "Hi, \nNice to meet you"
    recipient_list = recipient_list or ['contact@avtvn.com']
    ret = send_mail(subject, email_message, from_email, recipient_list, html_message=email_body_html,
                    fail_silently=False)
    return ret
