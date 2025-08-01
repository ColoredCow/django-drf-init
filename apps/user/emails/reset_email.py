from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.user.models import CustomUser


def send_password_reset_email(user: CustomUser):
    """Generate a one-time reset link and email it with contextual message to the user."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

    subject = "Reset Your Password"

    html_content = (
        f"<p>Dear User,</p>"
        f"<p>We received a request to reset your password.</p>"
        f"<p>To set a new password, please click the link below:<br>"
        f"<a href='{reset_link}'>Reset Your Password</a></p>"
        f"<p>If you did not request this change, you can safely ignore this email—your existing password will remain unchanged.</p>"
        f"<p>For any support or queries, feel free to reach out.<br>"
        f"<p>Warm regards,<br>Team <br>"
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body="",  # omit plain text
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
