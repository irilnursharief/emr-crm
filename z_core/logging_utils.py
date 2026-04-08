"""
Logging utilities for the EMR CRM application.

This module provides helper functions for consistent logging across the application.
All logs include contextual information like user, request path, and timestamps.

Usage:
    from z_core.logging_utils import get_logger, log_user_action, log_error

    logger = get_logger('emr')
    logger.info("Something happened")

    # Or with context
    log_user_action(request, "created customer", {"customer_id": 123})
"""

import logging
import traceback
from functools import wraps
from typing import Any, Optional
from django.http import HttpRequest


def get_logger(name: str = "emr") -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name. Use 'emr' for general, 'emr.email' for email,
              'emr.pdf' for PDF operations.

    Returns:
        Logger instance

    Example:
        logger = get_logger('emr.email')
        logger.info("Email sent successfully")
    """
    return logging.getLogger(name)


def get_user_info(request: Optional[HttpRequest]) -> str:
    """
    Extract user information from request for logging.

    Returns a string like "user:admin (id:1)" or "user:anonymous"
    """
    if request is None:
        return "user:system"

    if hasattr(request, "user") and request.user.is_authenticated:
        return f"user:{request.user.username} (id:{request.user.id})"

    return "user:anonymous"


def get_request_info(request: Optional[HttpRequest]) -> str:
    """
    Extract request information for logging.

    Returns a string like "GET /repairs/123/"
    """
    if request is None:
        return "path:N/A"

    method = getattr(request, "method", "N/A")
    path = getattr(request, "path", "N/A")

    return f"{method} {path}"


def log_user_action(
    request: HttpRequest,
    action: str,
    details: Optional[dict] = None,
    logger_name: str = "emr",
) -> None:
    """
    Log a user action with context.

    Args:
        request: Django HttpRequest object
        action: Description of the action (e.g., "created customer")
        details: Optional dictionary with additional details
        logger_name: Which logger to use

    Example:
        log_user_action(request, "created customer", {"customer_id": 123})
        # Logs: "INFO user:admin (id:1) POST /customers/create/ | created customer | {'customer_id': 123}"
    """
    logger = get_logger(logger_name)
    user_info = get_user_info(request)
    request_info = get_request_info(request)

    message = f"{user_info} {request_info} | {action}"

    if details:
        message += f" | {details}"

    logger.info(message)


def log_error(
    request: Optional[HttpRequest],
    error: Exception,
    context: Optional[str] = None,
    logger_name: str = "emr",
) -> None:
    """
    Log an error with full context and traceback.

    Args:
        request: Django HttpRequest object (can be None)
        error: The exception that occurred
        context: Optional description of what was happening
        logger_name: Which logger to use

    Example:
        try:
            do_something()
        except Exception as e:
            log_error(request, e, "processing payment")
    """
    logger = get_logger(logger_name)
    user_info = get_user_info(request)
    request_info = get_request_info(request)

    message = f"{user_info} {request_info} | ERROR"

    if context:
        message += f" while {context}"

    message += f" | {type(error).__name__}: {str(error)}"

    # Log with traceback
    logger.error(message, exc_info=True)


def log_email_event(
    request: Optional[HttpRequest],
    event: str,
    recipient: str,
    subject: str,
    success: bool,
    error: Optional[str] = None,
) -> None:
    """
    Log an email event (sent, failed, etc.)

    Args:
        request: Django HttpRequest object
        event: Event type (e.g., "send_job_order", "send_quotation")
        recipient: Email recipient
        subject: Email subject
        success: Whether the operation succeeded
        error: Error message if failed

    Example:
        log_email_event(request, "send_job_order", "customer@email.com", "Job Order #0001", True)
    """
    logger = get_logger("emr.email")
    user_info = get_user_info(request)

    status = "SUCCESS" if success else "FAILED"
    message = f"{user_info} | {event} | {status} | to:{recipient} | subject:{subject}"

    if error:
        message += f" | error:{error}"

    if success:
        logger.info(message)
    else:
        logger.error(message)


def log_pdf_event(
    request: Optional[HttpRequest],
    event: str,
    document_type: str,
    document_id: int,
    success: bool,
    duration_ms: Optional[float] = None,
    error: Optional[str] = None,
) -> None:
    """
    Log a PDF generation event.

    Args:
        request: Django HttpRequest object
        event: Event type (e.g., "generate", "download")
        document_type: Type of document (e.g., "job_order", "quotation")
        document_id: ID of the related record
        success: Whether the operation succeeded
        duration_ms: Time taken in milliseconds
        error: Error message if failed

    Example:
        log_pdf_event(request, "generate", "job_order", 123, True, duration_ms=1500)
    """
    logger = get_logger("emr.pdf")
    user_info = get_user_info(request)

    status = "SUCCESS" if success else "FAILED"
    message = f"{user_info} | {event} | {status} | {document_type}:{document_id}"

    if duration_ms is not None:
        message += f" | duration:{duration_ms:.0f}ms"

    if error:
        message += f" | error:{error}"

    if success:
        logger.info(message)
    else:
        logger.error(message)


def log_payment_event(
    request: HttpRequest,
    event: str,
    repair_id: int,
    amount: float,
    payment_type: str,
    success: bool,
    error: Optional[str] = None,
) -> None:
    """
    Log a payment event.

    Args:
        request: Django HttpRequest object
        event: Event type (e.g., "create", "refund")
        repair_id: ID of the repair
        amount: Payment amount
        payment_type: Type of payment
        success: Whether the operation succeeded
        error: Error message if failed

    Example:
        log_payment_event(request, "create", 123, 1500.00, "full_settlement", True)
    """
    logger = get_logger("emr")
    user_info = get_user_info(request)

    status = "SUCCESS" if success else "FAILED"
    message = f"{user_info} | payment_{event} | {status} | repair:{repair_id} | amount:{amount:.2f} | type:{payment_type}"

    if error:
        message += f" | error:{error}"

    if success:
        logger.info(message)
    else:
        logger.error(message)
