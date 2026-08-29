# backend/video_engine/adapters/flickr.py
"""Flickr server adapter — works via direct iframe + proxy."""
import asyncio
from playwright.async_api import async_playwright
from .base import resolve_episode_url, navigate_episode, click_server_option, resolve_iframe_chain, HEADERS

async def resolve_flickr(episode_url: str) -> dict:
    full_url = await resolve_episode_url(episode_url)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-dev-shm-usage", "--no-sandbox"])
        ctx = await browser.new_context(user_agent=HEADERS["User-Agent"])
        page = await ctx.new_page()
        try:
            await navigate_episode(page, full_url)
            await click_server_option(page, 'flickr')
            video_url = await resolve_iframe_chain(page)
            return {"server": "Flickr", "video_url": video_url, "embed_ready": bool(video_url), "success": bool(video_url)}
        except Exception as e:
            return {"server": "Flickr", "video_url": "", "success": False, "error": str(e)}
        finally:
            await browser.close()
    return {"server": "Flickr", "video_url": "", "success": False, "error": "Browser failed"}
