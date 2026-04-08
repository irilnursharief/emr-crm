from django.core.mail import EmailMessage
from django.conf import settings


def send_document_email(
    to_email: str,
    subject: str,
    body: str,
    pdf_bytes: bytes,
    filename: str,
) -> bool:
    """
    Sends an email with a PDF attachment.

    Returns True if successful, False if failed.
    """
    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )

        # Attach the PDF
        email.attach(filename, pdf_bytes, "application/pdf")

        email.send(fail_silently=False)
        return True

    except Exception as e:
        print(f"Email sending failed: {e}")
        return False
