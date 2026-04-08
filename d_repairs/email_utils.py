"""
Email utilities for sending documents to customers.

This module handles all email sending operations with proper logging
and error handling.
"""

import time
from django.core.mail import EmailMessage
from django.conf import settings
from z_core.logging_utils import get_logger, log_email_event

logger = get_logger("emr.email")


def send_document_email(
    to_email: str,
    subject: str,
    body: str,
    pdf_bytes: bytes,
    filename: str,
    request=None,
    event_type: str = "send_document",
) -> bool:
    """
    Sends an email with a PDF attachment.

    Args:
        to_email: Recipient email address
        subject: Email subject line
        body: Email body text
        pdf_bytes: PDF file contents as bytes
        filename: Name for the attached file
        request: Django request object (for logging context)
        event_type: Type of event for logging (e.g., "send_job_order")

    Returns:
        True if successful, False if failed.

    Example:
        success = send_document_email(
            to_email="customer@example.com",
            subject="Your Job Order",
            body="Please find attached...",
            pdf_bytes=pdf_content,
            filename="job-order-0001.pdf",
            request=request,
            event_type="send_job_order"
        )
    """
    start_time = time.time()

    try:
        logger.debug(f"Preparing email to {to_email} with subject: {subject}")

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )

        # Attach the PDF
        email.attach(filename, pdf_bytes, "application/pdf")

        logger.debug(f"Sending email to {to_email}...")
        email.send(fail_silently=False)

        duration_ms = (time.time() - start_time) * 1000

        log_email_event(
            request=request,
            event=event_type,
            recipient=to_email,
            subject=subject,
            success=True,
        )

        logger.info(f"Email sent successfully to {to_email} in {duration_ms:.0f}ms")
        return True

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        error_message = str(e)

        log_email_event(
            request=request,
            event=event_type,
            recipient=to_email,
            subject=subject,
            success=False,
            error=error_message,
        )

        logger.error(
            f"Email sending failed to {to_email} after {duration_ms:.0f}ms: {error_message}",
            exc_info=True,
        )
        return False
