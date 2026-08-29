# stream.py
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

TARGET_DOMAIN = "https://anichin.moe"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": f"{TARGET_DOMAIN}/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

async def loading_animation(text: str, duration: float = 0.3):
    chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f"\r{C_PINK}[{chars[i % len(chars)]}]{RESET} {C_BLUE}{text}{RESET}...")
        sys.stdout.flush()
        await asyncio.sleep(0.04)
        i += 1
    sys.stdout.write(f"\r{C_PURPLE}[✓]{RESET} {C_BLUE}{text}{RESET} {C_PINK}DONE.{RESET}\n")
    sys.stdout.flush()

def print_banner():
    banner = r"""
 █████╗ ███╗   ██╗██╗ ██████╗██╗  ██╗██╗███╗   ██╗
██╔══██╗████╗  ██║██║██╔════╝██║  ██║██║████╗  ██║
███████║██╔██╗ ██║██║██║     ███████║██║██╔██╗ ██║
██╔══██║██║╚██╗██║██║██║     ██╔══██║██║██║╚██╗██║
██║  ██║██║ ╚████║██║╚██████╗██║  ██║██║██║ ╚████║
╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
                                                  
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 [Module]                -> Anichin Clean JSON Resolver (stream.py)
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
        return f"{TARGET_DOMAIN}/{slug}/"

    encoded_query = urllib.parse.quote(clean_query)
    search_url = f"{TARGET_DOMAIN}/?s={encoded_query}"
    
    try:
        res = requests.get(search_url, headers=HEADERS, timeout=6)
        if res.status_code != 200:
            return None
            
        soup = BeautifulSoup(res.text, 'html.parser')
        first_item = soup.select_one('div.utao a, article.bs a, div.bsx a, .kanan h2 a, .film-list li a, .excstl a, .bs header.entry-header a')
        if not first_item or not first_item.get('href'):
            return None
            
        matched_url = first_item.get('href')
        if not matched_url.startswith("http"):
            matched_url = f"{TARGET_DOMAIN}{matched_url}" if matched_url.startswith('/') else f"{TARGET_DOMAIN}/{matched_url}"
        
        if "episode" in matched_url.lower():
            return matched_url
            
        res_main = requests.get(matched_url, headers=HEADERS, timeout=6)
        if res_main.status_code == 200:
            soup_main = BeautifulSoup(res_main.text, 'html.parser')
            ep_latest = soup_main.select_one('div.episodelist ul li:first-child a, ul.daftarep li:first-child a, .eplister ul li:first-child a, .lister ul li:first-child a, span.eps a')
            if ep_latest and ep_latest.get('href'):
                ep_url = ep_latest.get('href')
                return ep_url if ep_url.startswith("http") else f"{TARGET_DOMAIN}{ep_url}"
                
        return matched_url
    except Exception:
        return None

async def main():
    print_banner()
    
    print(f"{C_PINK}[?]{RESET} {C_BLUE}Masukkan Judul, Slug Episode, atau URL Episode/Series (Anichin):{RESET}")
    user_input = input(f" {C_PURPLE}╰─>{RESET} ").strip()
    
    if not user_input:
        err_payload = {
            "creator": "Vexalyn Developer",
            "statusCode": 400,
            "status": "error",
            "message": "Waduh, input judul atau URL-nya jangan dikosongin dong bos!",
            "data": {}
        }
        print(f"\n{C_RED}[CRITICAL ERROR]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}400{RESET}")
        print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
        print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
        print(f"{C_RED}{json.dumps(err_payload, indent=4, ensure_ascii=False)}{RESET}\n")
        return

    await loading_animation("Menghubungkan ke Anichin", 0.3)
    await loading_animation("Mencari URL episode target", 0.3)

    t_start = time.time()
    target_url = resolve_episode_url_stable(user_input)
    
    if not target_url:
        err_payload = {
            "creator": "Vexalyn Developer",
            "statusCode": 404,
            "status": "error",
            "message": f"Duh, Zonk bro! Episode atau server untuk '{user_input}' tidak ditemukan di Anichin.",
            "data": {}
        }
        print(f"\n{C_RED}[CRITICAL ERROR]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}404{RESET}")
        print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
        print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
        print(f"{C_RED}{json.dumps(err_payload, indent=4, ensure_ascii=False)}{RESET}\n")
        return

    try:
        def _fetch():
            r = requests.get(target_url, headers=HEADERS, timeout=6)
            return r.text, r.status_code
        html_page, status_code = await asyncio.to_thread(_fetch)
    except Exception:
        status_code = 500
        html_page = None

    if not html_page or status_code != 200:
        err_code = status_code if isinstance(status_code, int) else 500
        err_payload = {
            "creator": "Vexalyn Developer",
            "statusCode": err_code,
            "status": "error",
            "message": "Gagal memuat halaman episode target.",
            "data": {}
        }
        print(f"\n{C_RED}[ERROR RESPONSE]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}{err_code}{RESET}\n")
        return

    soup = BeautifulSoup(html_page, 'html.parser')
    title_el = soup.select_one('h1.entry-title, .post-title h1, h1')
    title = title_el.text.strip() if title_el else "Unknown Episode"

    server_elements = soup.select('.mobius select option, .pushserver option, ul.player-server li, .select-server li, div.player_option, div.pselect select option, .server_option, .eps-item, select#select-server option')
    
    server_names = []
    for el in server_elements:
        name = el.text.strip()
        if name and "pilih server" not in name.lower():
            if name not in server_names:
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
    
    print(f"{C_PINK}[AVAILABLE SERVERS]:{RESET}")
    if server_names:
        for idx, name in enumerate(server_names, 1):
            print(f"  {idx}. {C_CYAN}{name}{RESET}")
    else:
        print(f"  {C_RED}Tidak ada server spesifik terdeteksi.{RESET}")
    print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")

    print(f"{C_PINK}[?]{RESET} {C_BLUE}Ketik nama server yang diinginkan (atau tekan ENTER untuk default):{RESET}")
    server_keyword = input(f" {C_PURPLE}╰─>{RESET} ").strip()

    print(f"\n{C_PINK}[*]{RESET} {C_BLUE}Mengekstrak iframe untuk server '{server_keyword if server_keyword else 'Default'}'...{RESET}")
    start_time = time.time()

    iframe_url = None

    if not server_keyword:
        _iframe_static = soup.select_one('iframe, .pframe iframe, div.player-embed iframe, div#pframe iframe')
        if _iframe_static:
            _src = _iframe_static.get('src') or _iframe_static.get('data-src')
            if _src and "googleads" not in _src:
                iframe_url = f"{TARGET_DOMAIN}{_src}" if _src.startswith('/') else _src
        
        execution_time = round(time.time() - start_time, 2)
        print(f"\n {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Server Terpilih : {C_CYAN}Default (Static Iframe){RESET}")
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Elapsed Time    : {C_CYAN}{execution_time} seconds{RESET}")
        print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
        
        final_output = {
            "creator": "Vexalyn Developer",
            "statusCode": 200,
            "status": "success",
            "message": "Berhasil mengambil data stream Anichin.",
            "data": {
                "title": title,
                "url": target_url,
                "selected_server": "Default (Static)",
                "iframe_url": iframe_url,
                "download_links": download_links
            }
        }
        print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
        print(f"{C_CYAN}{json.dumps(final_output, indent=4, ensure_ascii=False)}{RESET}")
        print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
        print(f"{C_PINK}[!] Operational complete. Anichin clean mode finished safely.{RESET}\n")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-dev-shm-usage", 
                "--no-sandbox", 
                "--disable-gpu", 
                "--disable-extensions",
                "--blink-settings=imagesEnabled=false"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            extra_http_headers={"Referer": f"{TARGET_DOMAIN}/"}
        )
        page = await context.new_page()

        try:
            await page.route("**/*.{png,jpg,jpeg,gif,svg,css,ico,woff,woff2,font,mp4,webm}", lambda route: route.abort())
            await page.route("**/ads/**", lambda route: route.abort())
            
            await page.goto(target_url, wait_until="domcontentloaded", timeout=4000)

            locators = page.locator('.mobius select option, .pushserver option, ul.player-server li, .select-server li, div.player_option, div.pselect select option, .server_option, .eps-item, select#select-server option')
            count = await locators.count()
            
            target_locator = None
            matched_name = "Unknown"

            for i in range(count):
                item = locators.nth(i)
                text = (await item.inner_text()).strip()
                if server_keyword.lower() in text.lower() and "pilih server" not in text.lower():
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
                
                try: await page.wait_for_selector('iframe', timeout=1500)
                except: await asyncio.sleep(0.1)

            current_html = await page.content()
            current_soup = BeautifulSoup(current_html, 'html.parser')
            
            iframe = current_soup.select_one('iframe, .pframe iframe, div.player-embed iframe, div#pframe iframe')
            if iframe:
                src = iframe.get('src') or iframe.get('data-src')
                if src and "googleads" not in src:
                    iframe_url = f"{TARGET_DOMAIN}{src}" if src.startswith('/') else src

            execution_time = round(time.time() - start_time, 2)

            print(f"\n {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
            print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Server Terpilih : {C_CYAN}{matched_name}{RESET}")
            print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Elapsed Time    : {C_CYAN}{execution_time} seconds{RESET}")
            print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
            
            final_output = {
                "creator": "Vexalyn Developer",
                "statusCode": 200,
                "status": "success",
                "message": f"Berhasil mengambil data stream Anichin untuk server '{matched_name}'.",
                "data": {
                    "title": title,
                    "url": target_url,
                    "selected_server": matched_name,
                    "iframe_url": iframe_url,
                    "download_links": download_links
                }
            }
            print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
            print(f"{C_CYAN}{json.dumps(final_output, indent=4, ensure_ascii=False)}{RESET}")

        except Exception as e:
            err_payload = {
                "creator": "Vexalyn Developer",
                "statusCode": 500,
                "status": "error",
                "message": f"Terjadi kesalahan saat ekstraksi: {str(e)}",
                "data": {}
            }
            print(f"\n{C_RED}[ERROR RESPONSE]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}500{RESET}")
            print(f"{C_RED}[REASON]{RESET} {C_CYAN}{err_payload['message']}{RESET}")

        await browser.close()

    print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
    print(f"{C_PINK}[!] Operational complete. Anichin clean mode finished safely.{RESET}\n")

if __name__ == "__main__":
    asyncio.run(main())