"""
PDF Generation Utility using Playwright

This module handles converting HTML pages to PDF documents using
a headless Chromium browser (via Playwright).
"""

import asyncio
import time
from django.conf import settings
from playwright.async_api import async_playwright
from d_repairs.signing import create_signed_url
from z_core.logging_utils import get_logger

logger = get_logger("emr.pdf")


async def _generate_pdf_async(url: str, timeout_ms: int = 30000) -> bytes:
    """
    Asynchronously generate a PDF from a URL using Playwright.

    Args:
        url: The URL to convert to PDF
        timeout_ms: Maximum time to wait for page load (default: 30 seconds)

    Returns:
        PDF file contents as bytes

    Raises:
        Exception: If page fails to load or PDF generation fails
    """
    signed_url = create_signed_url(url)

    logger.debug(f"Starting PDF generation for URL: {url}")

    browser = None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            try:
                page = await browser.new_page()

                logger.debug(f"Navigating to page...")
                await page.goto(
                    signed_url, wait_until="networkidle", timeout=timeout_ms
                )

                logger.debug(f"Generating PDF...")
                pdf_bytes = await page.pdf(
                    format="A4",
                    margin={
                        "top": "1.5cm",
                        "bottom": "1.5cm",
                        "left": "1.5cm",
                        "right": "1.5cm",
                    },
                    print_background=True,
                )

                logger.debug(
                    f"PDF generated successfully, size: {len(pdf_bytes)} bytes"
                )
                return pdf_bytes

            finally:
                if browser:
                    await browser.close()
                    logger.debug("Browser closed")

    except Exception as e:
        logger.error(f"PDF generation failed for {url}: {str(e)}", exc_info=True)
        raise Exception(f"PDF generation failed: {str(e)}") from e


def generate_pdf(url: str, timeout_ms: int = 30000) -> bytes:
    """
    Synchronous wrapper around the async PDF generator.

    This is the function you call from Django views.

    Args:
        url: The URL to convert to PDF
        timeout_ms: Maximum time to wait for page load (default: 30 seconds)

    Returns:
        PDF file contents as bytes
    """
    start_time = time.time()

    try:
        result = asyncio.run(_generate_pdf_async(url, timeout_ms))
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"PDF generated in {duration_ms:.0f}ms for {url}")
        return result
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            f"PDF generation failed after {duration_ms:.0f}ms for {url}: {str(e)}"
        )
        raise
