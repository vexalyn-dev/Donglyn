# backend/video_engine/adapters/dailymotion.py
"""Dailymotion server adapter."""
import asyncio
from playwright.async_api import async_playwright
from .base import resolve_episode_url, navigate_episode, click_server_option, resolve_iframe_chain, HEADERS

async def resolve_dailymotion(episode_url: str) -> dict:
    full_url = await resolve_episode_url(episode_url)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-dev-shm-usage", "--no-sandbox"])
        ctx = await browser.new_context(user_agent=HEADERS["User-Agent"])
        page = await ctx.new_page()
        try:
            await navigate_episode(page, full_url)
            await click_server_option(page, 'dailymotion')
            video_url = await resolve_iframe_chain(page)
            return {"server": "Dailymotion", "video_url": video_url, "embed_ready": bool(video_url and 'dailymotion' in video_url), "success": bool(video_url)}
        except Exception as e:
            return {"server": "Dailymotion", "video_url": "", "success": False, "error": str(e)}
        finally:
            await browser.close()
    return {"server": "Dailymotion", "video_url": "", "success": False, "error": "Browser failed"}
