# backend/video_engine/adapters/base.py
"""Base adapter dengan helper umum."""
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://anichin.moe/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

async def resolve_episode_url(url: str) -> str:
    """Normalize slug → full URL pakai stream.resolve_episode_url_stable."""
    from stream import resolve_episode_url_stable
    return resolve_episode_url_stable(url) or url

async def navigate_episode(page, url: str):
    """Navigate episode page, abort heavy resources."""
    await page.route("**/*.{png,jpg,jpeg,gif,svg,css,ico,woff,woff2,mp4,webm}", lambda r: r.abort())
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(1.5)

async def click_server_option(page, keyword: str):
    """Click server option by keyword."""
    locators = page.locator('.mobius select option, .pushserver option, ul.player-server li, .select-server li, div.player_option, .server_option')
    count = await locators.count()
    for i in range(count):
        item = locators.nth(i)
        text = (await item.inner_text()).strip()
        if keyword.lower() in text.lower():
            tag = await item.evaluate("el => el.tagName.toLowerCase()")
            if tag == "option":
                parent = item.locator("xpath=ancestor::select")
                if await parent.count() > 0:
                    val = await item.get_attribute("value")
                    if val:
                        await parent.select_option(value=val)
                    else:
                        await item.click(force=True)
                else:
                    await item.click(force=True)
            else:
                await item.click(force=True)
            await asyncio.sleep(2)
            return True
    return False

async def resolve_iframe_chain(page, max_iter=4):
    """Navigate iframe chain to get final video URL."""
    video_url = ""
    for _ in range(max_iter):
        html = await page.content()
        if "403" in html and len(html) < 5000:
            break
        soup = BeautifulSoup(html, 'html.parser')
        iframe = soup.select_one('iframe[src], iframe[data-src]')
        if not iframe:
            break
        src = iframe.get('src') or iframe.get('data-src') or ""
        if not src or "googleads" in src:
            break
        src_url = src if src.startswith('http') else f"https://anichin.moe{src}"
        # Stop if URL is not a stream/player intermediary
        if '/stream/' not in src_url and 'anichin-player' not in src_url:
            video_url = src_url
            break
        resp = await page.goto(src_url, wait_until="domcontentloaded", timeout=20000)
        if resp and resp.status == 403:
            break
        await asyncio.sleep(1.5)

    # Final extraction
    if not video_url:
        final_html = await page.content()
        final_soup = BeautifulSoup(final_html, 'html.parser')
        final_iframe = final_soup.select_one('iframe[src], iframe[data-src]')
        if final_iframe:
            video_url = final_iframe.get('src') or final_iframe.get('data-src') or ""
            if video_url.startswith('//'):
                video_url = 'https:' + video_url
            elif video_url.startswith('/'):
                video_url = 'https://anichin.moe' + video_url
        # Also check <video> tag
        if not video_url:
            video_tag = final_soup.select_one('video')
            if video_tag:
                video_url = video_tag.get('src') or ''

    return video_url
