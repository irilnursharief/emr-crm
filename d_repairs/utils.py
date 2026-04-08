"""
PDF Generation Utility using Playwright

This module handles converting HTML pages to PDF documents using
a headless Chromium browser (via Playwright).

The process:
1. Receive a URL to convert
2. Add a signed URL parameter (so the headless browser can access protected pages)
3. Launch headless Chromium
4. Navigate to the page and wait for it to fully load
5. Generate PDF with specified margins and format
6. Close browser and return PDF bytes
"""

import asyncio
from django.conf import settings
from playwright.async_api import async_playwright
from d_repairs.signing import create_signed_url


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
    # Create a signed URL so the headless browser can access the page
    signed_url = create_signed_url(url)

    browser = None

    try:
        # Start Playwright and launch Chromium
        async with async_playwright() as p:
            # Launch browser
            # headless=True means no visible window (runs in background)
            browser = await p.chromium.launch(headless=True)

            try:
                # Create a new browser page (like a new tab)
                page = await browser.new_page()

                # Navigate to the URL
                # wait_until="networkidle" means wait until no network requests for 500ms
                # This ensures all CSS, images, and fonts are loaded
                await page.goto(
                    signed_url, wait_until="networkidle", timeout=timeout_ms
                )

                # Generate PDF
                pdf_bytes = await page.pdf(
                    format="A4",
                    margin={
                        "top": "1.5cm",
                        "bottom": "1.5cm",
                        "left": "1.5cm",
                        "right": "1.5cm",
                    },
                    print_background=True,  # Include background colors/images
                )

                return pdf_bytes

            finally:
                # IMPORTANT: Always close browser, even if an error occurred
                # This prevents zombie browser processes from accumulating
                if browser:
                    await browser.close()

    except Exception as e:
        # Re-raise with more context for debugging
        raise Exception(f"PDF generation failed for {url}: {str(e)}") from e


def generate_pdf(url: str, timeout_ms: int = 30000) -> bytes:
    """
    Synchronous wrapper around the async PDF generator.

    This is the function you call from Django views.

    Args:
        url: The URL to convert to PDF
        timeout_ms: Maximum time to wait for page load (default: 30 seconds)

    Returns:
        PDF file contents as bytes

    Example:
        pdf_bytes = generate_pdf("http://localhost:8000/repairs/1/job-order/")
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
    """
    return asyncio.run(_generate_pdf_async(url, timeout_ms))
