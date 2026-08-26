# episode.py
import sys
import asyncio
import json
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# ANSI Colors - Tema Pink, Ungu, Biru
C_PURPLE = "\033[35m"
C_PINK = "\033[95m"
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"
C_RED = "\033[91m"
RESET = "\033[0m"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://anichin.moe/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def print_banner():
    banner = r"""
8888888b.   .d88888b.  888b    888  .d8888b.  888    888 888     888      d8888       .d8888b.   .d8888b.  8888888b.         d8888 8888888b.  8888888888 8888888b.  
888  "Y88b d88P" "Y88b 8888b   888 d88P  Y88b 888    888 888     888     d88888      d88P  Y88b d88P  Y88b 888   Y88b       d88888 888   Y88b 888        888   Y88b 
888    888 888     888 88888b  888 888    888 888    888 888     888    d88P888      Y88b.      888    888 888    888      d88P888 888    888 888        888    888 
888    888 888     888 888Y88b 888 888        8888888888 888     888   d88P 888       "Y888b.   888        888   d88P     d88P 888 888   d88P 8888888    888   d88P 
888    888 888     888 888 Y88b888 888  88888 888    888 888     888  d88P  888          "Y88b. 888        8888888P"     d88P  888 8888888P"  888        8888888P"  
888    888 888     888 888  Y88888 888    888 888    888 888     888 d88P   888            "888 888    888 888 T88b     d88P   888 888        888        888 T88b   
888  .d88P Y88b. .d88P 888   Y8888 Y88b  d88P 888    888 Y8b. .d88P d8888888888      Y88b  d88P Y88b  d88P 888  T88b   d8888888888 888        888        888  T88b  
8888888P"   "Y88888P"  888    Y888  "Y8888P88 888    888  "Y88888P" d88P     888       "Y8888P"   "Y8888P"  888   T88b d88P     888 888        8888888888 888   T88b 
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 [Module]                -> Stable & Fast Search Resolver (episode.py)
 [Target Endpoint]       -> https://anichin.moe
 [Developer]             -> Vexalyn Developer
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────"""
    print(f"{C_PURPLE}{banner}{RESET}")

def resolve_episode_url_stable(query: str):
    clean_query = query.strip()
    if clean_query.startswith("http"):
        return clean_query
        
    if "episode" in clean_query.lower():
        slug = clean_query.lower().strip('/')
        slug = "".join([c if c.isalnum() or c.isspace() else "" for c in slug])
        slug = "-".join(slug.split())
        return f"https://anichin.moe/{slug}/"

    encoded_query = urllib.parse.quote(clean_query)
    search_url = f"https://anichin.moe/?s={encoded_query}"
    
    try:
        res = requests.get(search_url, headers=HEADERS, timeout=5)
        if res.status_code != 200:
            return None
            
        soup = BeautifulSoup(res.text, 'html.parser')
        first_item = soup.select_one('div.utao a, article.bs a, div.bsx a, .kanan h2 a, .film-list li a')
        if not first_item or not first_item.get('href'):
            return None
            
        matched_url = first_item.get('href')
        if not matched_url.startswith("http"):
            matched_url = f"https://anichin.moe{matched_url}" if matched_url.startswith('/') else f"https://anichin.moe/{matched_url}"
        
        if "episode" in matched_url.lower():
            return matched_url
            
        res_main = requests.get(matched_url, headers=HEADERS, timeout=5)
        if res_main.status_code == 200:
            soup_main = BeautifulSoup(res_main.text, 'html.parser')
            ep_latest = soup_main.select_one('div.episodelist ul li:first-child a, ul.daftarep li:first-child a, .eplister ul li:first-child a')
            if ep_latest and ep_latest.get('href'):
                ep_url = ep_latest.get('href')
                return ep_url if ep_url.startswith("http") else f"https://anichin.moe{ep_url}"
                
        return matched_url
    except Exception:
        return None

async def main():
    print_banner()
    
    print(f"{C_PINK}[?]{RESET} {C_BLUE}Masukkan Judul, Slug Episode, atau URL Episode:{RESET}")
    user_input = input(f" {C_PURPLE}╰─>{RESET} ").strip()
    
    if not user_input:
        print(f"{C_RED}[!] Input tidak boleh kosong.{RESET}")
        return

    t_start = time.time()
    target_url = resolve_episode_url_stable(user_input)
    
    if not target_url:
        print(f"{C_RED}[CRITICAL ERROR] Episode atau server untuk '{user_input}' tidak ditemukan.{RESET}")
        return

    try:
        res_page = requests.get(target_url, headers=HEADERS, timeout=5)
        html_page = res_page.text
    except Exception as e:
        print(f"{C_RED}[CRITICAL ERROR] Gagal memuat halaman: {str(e)}{RESET}")
        return

    soup = BeautifulSoup(html_page, 'html.parser')
    title_el = soup.select_one('h1.entry-title, .post-title h1, h1')
    title = title_el.text.strip() if title_el else "Unknown Episode"

    server_elements = soup.select('.mobius select option, .pushserver option, ul.player-server li, .select-server li, div.player_option, div.pselect select option, .server_option, .eps-item, select#select-server option')
    
    server_names = []
    for el in server_elements:
        name = el.text.strip()
        if name and name.lower() != " pilih server video ":
            server_names.append(name)

    if not server_names and soup.select('iframe, .pframe iframe'):
        server_names.append("Default Server (Iframe)")

    download_links = []
    download_rows = soup.select('div.soraddlx div.soraurlx, div.soraurlx')
    for row in download_rows:
        strong_el = row.find('strong')
        resolution = strong_el.text.strip().upper() if strong_el else "HD"
        servers = []
        for a in row.find_all('a'):
            server_name = a.text.strip()
            server_url = a.get('href')
            if server_url and "javascript" not in server_url:
                servers.append({"server_name": server_name, "url": server_url})
        if servers:
            download_links.append({"resolution": resolution, "servers": servers})

    resolve_time = round(time.time() - t_start, 2)

    print(f"\n {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
    print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Episode Title : {C_CYAN}{title}{RESET}")
    print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Resolved URL  : {C_CYAN}{target_url}{RESET}")
    print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Resolve Time  : {C_CYAN}{resolve_time} seconds{RESET}")
    print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
    
    print(f"{C_PINK}[AVAILABLE SERVERS DI HALAMAN INI]:{RESET}")
    for name in server_names:
        print(f"  • {C_CYAN}{name}{RESET}")
    print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")

    print(f"{C_PINK}[?]{RESET} {C_BLUE}Ketik nama server yang diinginkan (Contoh: Okru, Dailymotion, Odysee):{RESET}")
    server_keyword = input(f" {C_PURPLE}╰─>{RESET} ").strip()

    if not server_keyword:
        print(f"{C_RED}[!] Nama server tidak boleh kosong.{RESET}")
        return

    print(f"\n{C_PINK}[*]{RESET} {C_BLUE}Mengekstrak iframe untuk server '{server_keyword}'...{RESET}")
    start_time = time.time()

    iframe_url = None
    # fast pre-check: kalau halaman sudah punya iframe statis dan user minta server default, skip browser
    _soup_static = soup
    _iframe_static = _soup_static.select_one('iframe, .pframe iframe, div.player-embed iframe')
    if _iframe_static:
        _src = _iframe_static.get('src') or _iframe_static.get('data-src')
        if _src and "googleads" not in _src and server_keyword.lower() in ["default","auto","iframe","player"]:
            iframe_url = f"https://anichin.moe{_src}" if _src.startswith('/') else _src
            execution_time = round(time.time() - start_time, 2)
            print(f"\n {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
            print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Server Terpilih : {C_CYAN}Default (Static Iframe - No Browser){RESET}")
            print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Elapsed Time    : {C_CYAN}{execution_time} seconds{RESET}")
            print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
            final_output = {"creator": "Vexalyn Developer","statusCode": 200,"status": "success","data": {"title": title,"url": target_url,"selected_server": "Default (Static)","iframe_fallback": iframe_url,"download_links": download_links}}
            print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
            print(f"{C_CYAN}{json.dumps(final_output, indent=4, ensure_ascii=False)}{RESET}")
            print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
            print(f"{C_PINK}[!] Operational complete. Vexalyn Scraper core closed safely.{RESET}\n")
            return

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu", "--blink-settings=imagesEnabled=false"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            await page.route("**/*.{png,jpg,jpeg,gif,svg,css,ico,woff,woff2,font}", lambda route: route.abort())
            await page.goto(target_url, wait_until="domcontentloaded", timeout=10000)
            await asyncio.sleep(0.3)

            locators = page.locator('.mobius select option, .pushserver option, ul.player-server li, .select-server li, div.player_option, div.pselect select option, .server_option, .eps-item, select#select-server option')
            count = await locators.count()
            
            target_locator = None
            matched_name = "Unknown"

            for i in range(count):
                item = locators.nth(i)
                text = (await item.inner_text()).strip()
                if server_keyword.lower() in text.lower():
                    target_locator = item
                    matched_name = text
                    break

            if target_locator:
                tag_name = await target_locator.evaluate("el => el.tagName.toLowerCase()")
                if tag_name == "option":
                    parent_select = target_locator.locator("xpath=ancestor::select")
                    if await parent_select.count() > 0:
                        val = await target_locator.get_attribute("value")
                        await parent_select.select_option(value=val)
                    else:
                        await target_locator.click(force=True)
                else:
                    await target_locator.click(force=True)
                
                try: await page.wait_for_selector('iframe', timeout=2500)
                except: await asyncio.sleep(0.4)
            else:
                if count > 0:
                    first_item = locators.nth(0)
                    matched_name = (await first_item.inner_text()).strip() + " (Fallback First)"
                    await first_item.click(force=True)
                    try: await page.wait_for_selector('iframe', timeout=2500)
                    except: await asyncio.sleep(0.4)

            current_html = await page.content()
            current_soup = BeautifulSoup(current_html, 'html.parser')
            
            iframe = current_soup.select_one('iframe, .pframe iframe, div.player-embed iframe, div#pframe iframe')
            if iframe:
                src = iframe.get('src') or iframe.get('data-src')
                if src and "googleads" not in src:
                    iframe_url = f"https://anichin.moe{src}" if src.startswith('/') else src

            execution_time = round(time.time() - start_time, 2)

            print(f"\n {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
            print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Server Terpilih : {C_CYAN}{matched_name}{RESET}")
            print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Elapsed Time    : {C_CYAN}{execution_time} seconds{RESET}")
            print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
            
            final_output = {
                "creator": "Vexalyn Developer",
                "statusCode": 200,
                "status": "success",
                "data": {
                    "title": title,
                    "url": target_url,
                    "selected_server": matched_name,
                    "iframe_fallback": iframe_url,
                    "download_links": download_links
                }
            }
            print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
            print(f"{C_CYAN}{json.dumps(final_output, indent=4, ensure_ascii=False)}{RESET}")

        except Exception as e:
            print(f"{C_RED}[CRITICAL ERROR] Terjadi kesalahan: {str(e)}{RESET}")

        await browser.close()

    print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
    print(f"{C_PINK}[!] Operational complete. Vexalyn Scraper core closed safely.{RESET}\n")

if __name__ == "__main__":
    asyncio.run(main())