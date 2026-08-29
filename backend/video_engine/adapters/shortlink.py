# backend/video_engine/adapters/shortlink.py
import asyncio
import re
from playwright.async_api import async_playwright

TARGET_DOMAIN = "https://anichin.moe"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": f"{TARGET_DOMAIN}/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


async def bypass_shortlink(shortlink_url: str) -> str:
    """
    Navigate through shortlink pages (pixeldrain, zippyshare, etc.)
    Click 'Continue' / 'Get Link' button and return final URL.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-gpu",
                "--blink-settings=imagesEnabled=false",
            ],
        )
        context = await browser.new_context(user_agent=HEADERS["User-Agent"])
        page = await context.new_page()

        try:
            await page.route("**/*.{png,jpg,jpeg,gif,svg,css,ico,woff,woff2,font,mp4,webm}", lambda route: route.abort())
            await page.goto(shortlink_url, wait_until="domcontentloaded", timeout=20000)

            # Try to click continue/get link button
            buttons = [
                'text=Continue',
                'text=Continue to',
                'text=Get Link',
                'text=Download',
                'text=Click Here',
                'button[type="submit"]',
                '.btn-primary',
                '#downloadBtn',
                '#continueBtn',
            ]

            clicked = False
            for selector in buttons:
                try:
                    el = page.locator(selector).first
                    if await el.count() > 0 and await el.is_visible():
                        await el.click(force=True)
                        clicked = True
                        break
                except Exception:
                    continue

            if clicked:
                try:
                    await page.wait_for_url("**/*", timeout=10000)
                except Exception:
                    await asyncio.sleep(2)

            final_url = page.url
            if final_url == shortlink_url:
                # Try to extract URL from page content
                html = await page.content()
                url_match = re.search(r'(https?://[^"\'>\s]+\.(mp4|webm|mkv|avi|mov))', html, re.IGNORECASE)
                if url_match:
                    return url_match.group(1)
                link_match = re.search(r'href=["\']([^"\']+(?:mp4|webm|mkv|avi|mov)[^"\']*)["\']', html, re.IGNORECASE)
                if link_match:
                    return link_match.group(1)

            return final_url
        except Exception as e:
            return f"error:{str(e)}"
        finally:
            await browser.close()
