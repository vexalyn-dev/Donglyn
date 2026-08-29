# status.py
import sys
import asyncio
import json
import time
import requests
from bs4 import BeautifulSoup
from core.browser import get_page_content
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

async def get_page_content_fast(url: str):
    def _fetch():
        try:
            r = requests.get(url, headers=HEADERS, timeout=8)
            if r.status_code == 200:
                txt = r.text
                if "Just a moment" in txt or "cf-challenge" in txt.lower():
                    return None, 403
                return txt, 200
            return None, r.status_code
        except Exception:
            return None, 500
    
    res = await asyncio.to_thread(_fetch)
    if isinstance(res, tuple) and len(res) == 2:
        html, code = res
        if html:
            return html, None, code
    
    fallback_html = await get_page_content(url)
    return fallback_html, None, 200

async def loading_animation(text: str, duration: float = 1.0):
    chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f"\r{C_PINK}[{chars[i % len(chars)]}]{RESET} {C_BLUE}{text}{RESET}...")
        sys.stdout.flush()
        await asyncio.sleep(0.1)
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
 [Module]                -> All Status Options Scraper Core (status.py)
 [Target Endpoint]       -> https://anichin.moe/anime/
 [Developer]             -> Vexalyn Developer
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────"""
    print(f"{C_PURPLE}{banner}{RESET}")

async def scrape_all_status():
    target_url = "https://anichin.moe/anime/"
    t_start = time.time()
    
    html_content, _, status_code = await get_page_content_fast(target_url)
    elapsed = round(time.time() - t_start, 2)
    
    if not html_content or status_code != 200:
        return {
            "creator": "Vexalyn Developer",
            "statusCode": status_code if status_code else 500,
            "status": "error",
            "message": "Gagal narik data status karena server timeout atau diblokir.",
            "elapsed_time": f"{elapsed} seconds",
            "total_status": 0,
            "data": []
        }

    soup = BeautifulSoup(html_content, 'html.parser')
    status_elements = soup.select('select[name="status"] option, select[name*="status"] option, input[name*="status"], .filter-status input')
    
    status_list = [{"name": "All", "slug": "all"}]
    seen_slugs = {"all"}
    
    for el in status_elements:
        if el.name == 'option':
            raw_val = el.get('value', '').strip()
            raw_text = el.text.strip()
        elif el.name == 'input':
            raw_val = el.get('value', '').strip()
            label = el.find_next_sibling('label') or el.parent
            raw_text = label.text.strip() if label else raw_val
        else:
            continue

        if raw_val and raw_val.lower() not in ["", "all", "0"]:
            slug = raw_val.lower().replace(" ", "-")
            clean_name = raw_text.strip() or slug.capitalize()
            if slug not in seen_slugs:
                seen_slugs.add(slug)
                status_list.append({"name": clean_name, "slug": slug})

    if len(status_list) == 1:
        status_list.extend([
            {"name": "Ongoing", "slug": "ongoing"},
            {"name": "Completed", "slug": "completed"}
        ])

    return {
        "creator": "Vexalyn Developer",
        "statusCode": 200,
        "status": "success",
        "message": f"Mantap! Berhasil menarik {len(status_list)} daftar status dari Anichin.",
        "elapsed_time": f"{elapsed} seconds",
        "total_status": len(status_list),
        "data": status_list
    }

async def main():
    print_banner()
    await loading_animation("Membangun koneksi ke Anichin", 0.4)
    await loading_animation("Mengekstrak data filter status", 0.6)
    
    start_time = time.time()
    result = await scrape_all_status()
    execution_time = round(time.time() - start_time, 2)
    
    print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
    print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}{result['statusCode']}{RESET}")
    print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Total Status:{RESET} {C_CYAN}{result.get('total_status', 0)} items{RESET}")
    print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Elapsed Time:{RESET} {C_CYAN}{execution_time} seconds{RESET}")
    print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
    print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
    print(f"{C_CYAN}{json.dumps(result, indent=4, ensure_ascii=False)}{RESET}\n")

if __name__ == "__main__":
    asyncio.run(main())