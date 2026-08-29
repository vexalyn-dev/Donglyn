# latest.py
import sys
import asyncio
import json
import time
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://anichin.moe/"
}

# ANSI Colors - Tema Pink, Ungu, Biru
C_PURPLE = "\033[35m"  # Ungu gelap
C_PINK = "\033[95m"    # Magenta / Pink terang
C_BLUE = "\033[94m"    # Biru terang
C_CYAN = "\033[96m"    # Biru Cyan
C_RED = "\033[91m"     # Merah (buat error)
RESET = "\033[0m"

async def loading_animation(text: str, duration: float = 2.0):
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
 [Module]                -> Latest Series Update Scraper (latest.py)
 [Target Endpoint]       -> https://anichin.moe/anime/?order=update
 [Developer]             -> Vexalyn Developer
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────"""
    print(f"{C_PURPLE}{banner}{RESET}")

async def scrape_latest_series(page: int):
    if page == 1:
        target_url = "https://anichin.moe/anime/?status=&type=&order=update"
    else:
        target_url = f"https://anichin.moe/anime/page/{page}/?status=&type=&order=update"
        
    def _fetch():
        try:
            r = requests.get(target_url, headers=HEADERS, timeout=10)
            return r.text, r.status_code
        except requests.exceptions.Timeout:
            return None, 504
        except requests.exceptions.ConnectionError:
            return None, 503
        except Exception:
            return None, 500
            
    html_content, status_code = await asyncio.to_thread(_fetch)
    
    if not html_content or status_code != 200:
        err_code = status_code if isinstance(status_code, int) else 500
        
        if err_code == 403 or (html_content and ("Just a moment" in html_content or "cf-challenge" in html_content.lower())):
            err_code = 403
            err_msg = "Yah, diblokir Cloudflare target nih. Coba lagi nanti atau ganti jaringan."
        elif err_code == 404:
            err_msg = "Waduh, halaman direktori update gak ketemu di server."
        elif err_code == 503:
            err_msg = "Duh, server Anichin-nya lagi ngambek atau down tuh."
        elif err_code == 504:
            err_msg = "Koneksi nyangkut alias timeout, kelamaan nunggu balasan dari server target."
        else:
            err_msg = f"Gagal narik halaman update, server merespon dengan status code {err_code}."

        return {
            "creator": "Vexalyn Developer",
            "statusCode": err_code,
            "status": "error",
            "message": err_msg,
            "ok": False,
            "current_page": page,
            "max_page": 1,
            "total_data": 0,
            "data": []
        }

    soup = BeautifulSoup(html_content, 'html.parser')
    latest_items = []
    seen_urls = set()
    
    items = soup.select('div.bsx')
    
    for item in items:
        try:
            a_tag = item.select_one('a')
            img_tag = item.select_one('img')
            title_tag = item.select_one('h2, .title, .tt')
            
            if not a_tag or not a_tag.get('href'): continue
            url = a_tag.get('href')
            if not url.startswith("http"):
                url = f"https://anichin.moe{url}" if url.startswith('/') else f"https://anichin.moe/{url}"
            
            raw_title = title_tag.text.strip() if title_tag else (a_tag.get('title') or "")
            if not raw_title and a_tag.get('title'):
                raw_title = a_tag.get('title')
            
            clean_title = re.sub(r'\s*Episode\s+\d+.*$', '', raw_title, flags=re.IGNORECASE).strip()
            clean_title = re.sub(r'\s*\[?END\]?.*$', '', clean_title, flags=re.IGNORECASE).strip()
            clean_title = re.sub(r'\s*Tamat.*$', '', clean_title, flags=re.IGNORECASE).strip()
            clean_title = re.sub(r'\s*Subtitle\s+Indonesia.*$', '', clean_title, flags=re.IGNORECASE).strip()
            
            length = len(clean_title)
            half = length // 2
            if length % 2 == 0 and clean_title[:half] == clean_title[half:]:
                title = clean_title[:half]
            else:
                title = clean_title if clean_title else "Tanpa Judul"

            thumbnail = ""
            if img_tag:
                thumbnail = img_tag.get('data-src') or img_tag.get('data-lazy-src') or img_tag.get('src') or ""
                if not thumbnail and img_tag.get('srcset'):
                    thumbnail = img_tag.get('srcset').split(',')[0].split()[0]
            
            type_val = "Donghua"
            type_elem = item.select_one('.typez')
            if type_elem and type_elem.text.strip():
                type_val = type_elem.text.strip()
            
            label_val = "Sub"
            label_elem = item.select_one('.sub, span.sub')
            if label_elem and label_elem.text.strip():
                label_val = label_elem.text.strip()
            
            status_val = "Ongoing"
            status_elem = item.select_one('.epx, .status')
            if status_elem and status_elem.text.strip():
                status_val = status_elem.text.strip()

            if url not in seen_urls:
                seen_urls.add(url)
                latest_items.append({
                    "title": title,
                    "url": url,
                    "thumbnail": thumbnail,
                    "type": type_val,
                    "label": label_val,
                    "status": status_val
                })
        except Exception:
            continue
            
    max_page = 1
    pagination_links = soup.select('.pagination a.page-numbers')
    for p in pagination_links:
        if p.text.isdigit():
            max_page = max(max_page, int(p.text))
            
    total_data = len(latest_items)
    
    if total_data == 0:
        return {
            "creator": "Vexalyn Developer",
            "statusCode": 404,
            "status": "error",
            "message": f"Duh, Zonk bro! Gak ada data sama sekali di halaman {page}.",
            "ok": False,
            "current_page": page,
            "max_page": max_page,
            "total_data": 0,
            "data": []
        }

    return {
        "creator": "Vexalyn Developer",
        "statusCode": 200,
        "status": "success",
        "message": f"Mantap! Berhasil nyomot update series buat Halaman {page}",
        "ok": True,
        "current_page": page,
        "max_page": max_page,
        "total_data": total_data,
        "data": latest_items
    }

async def main():
    print_banner()
    
    print(f"{C_PINK}[?]{RESET} {C_BLUE}Masukkan nomor halaman yang ingin di-scrape (contoh: 1):{RESET}")
    page_input = input(f" {C_PURPLE}╰─>{RESET} ").strip()
    
    if page_input and not page_input.isdigit():
        print(f"\n{C_RED}[CRITICAL ERROR]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}400{RESET}")
        print(f"{C_RED}[REASON]{RESET} {C_CYAN}Waduh, nomor halaman harus diisi angka yang bener dong!{RESET}")
        return

    page = int(page_input) if page_input else 1
    if page < 1: page = 1

    await loading_animation("Membangun koneksi ke Anichin", 0.5)
    await loading_animation(f"Lagi nyari data direktori series untuk Halaman {page}", 0.5)
    
    print(f"\n{C_PINK}[*]{RESET} {C_BLUE}Processing payload hook onto target DOM structure...{RESET}")
    
    start_time = time.time()
    result = await scrape_latest_series(page)
    execution_time = round(time.time() - start_time, 2)
    
    print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
    if result["ok"]:
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}{result['statusCode']}{RESET}")
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Page Target:{RESET} {C_CYAN}{result['current_page']} (Max: {result['max_page']}){RESET}")
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Payload Size:{RESET} {C_CYAN}{result['total_data']} items extracted{RESET}")
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Elapsed Time:{RESET} {C_CYAN}{execution_time} seconds{RESET}")
        print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
        
        print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
        print(f"{C_CYAN}{json.dumps(result, indent=4, ensure_ascii=False)}{RESET}")
    else:
        print(f"{C_RED}[ERROR RESPONSE]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}{result['statusCode']}{RESET}")
        print(f"{C_RED}[REASON]{RESET} {C_CYAN}{result['message']}{RESET}")
        print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
        print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
        print(f"{C_RED}{json.dumps(result, indent=4, ensure_ascii=False)}{RESET}")
    
    print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
    print(f"{C_PINK}[!] Operational complete. Vexalyn Scraper core closed safely.{RESET}\n")

if __name__ == "__main__":
    asyncio.run(main())