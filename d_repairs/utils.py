import asyncio
from django.conf import settings
from playwright.async_api import async_playwright
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse


def _build_pdf_url(url: str) -> str:
    """Add pdf_token to URL, replacing any existing one."""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    params.pop("pdf_token", None)
    params["pdf_token"] = [settings.PDF_SECRET_TOKEN]
    new_query = urlencode(params, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


async def _generate_pdf_async(url: str) -> bytes:
    url_with_token = _build_pdf_url(url)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto(url_with_token, wait_until="networkidle")

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

        await browser.close()
        return pdf_bytes


def generate_pdf(url: str) -> bytes:
    """
    Synchronous wrapper around the async Playwright PDF generator.
    Call this from Django views.
    """
    return asyncio.run(_generate_pdf_async(url))
