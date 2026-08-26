# core/browser.py
import asyncio
from playwright.async_api import async_playwright

async def get_page_content(url: str):
    """Mengambil HTML mentah dari URL target dengan kecepatan tinggi dan pemblokiran resource berat."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-dev-shm-usage", 
                "--no-sandbox", 
                "--disable-gpu",
                "--blink-settings=imagesEnabled=false"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Blokir resource yang tidak perlu (gambar, font, stylesheet) agar loading instan
        await page.route("**/*.{png,jpg,jpeg,svg,gif,webp,css,font,woff,woff2}", lambda route: route.abort())
        
        try:
            # Gunakan domcontentloaded agar langsung eksekusi begitu struktur DOM siap (tanpa tunggu resource luar)
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Pastikan elemen utama judul sudah termuat
            try:
                await page.wait_for_selector('h2[itemprop="partOfSeries"], .infolimit h2, .desc.mindes, h1.entry-title, h1', timeout=3000)
            except:
                pass
                
            html = await page.content()
            await browser.close()
            return html, None
        except Exception as e:
            await browser.close()
            return None, str(e)