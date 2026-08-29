# az_list.py
import sys
import asyncio
import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

# ANSI Colors - Tema Pink, Ungu, Biru
C_PURPLE = "\033[35m"  # Ungu gelap
C_PINK = "\033[95m"    # Magenta / Pink terang
C_BLUE = "\033[94m"    # Biru terang
C_CYAN = "\033[96m"    # Biru Cyan
C_RED = "\033[91m"     # Merah (buat error)
RESET = "\033[0m"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://anichin.moe/"
}

async def loading_animation(text: str, duration: float = 0.8):
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
    """
    print(f"{C_PURPLE}{banner}{RESET}")
    print("─" * 125)
    print(f" {C_PINK}[Module]{RESET}                -> A-Z List Scraper Core (Fixed # & 0-9)")
    print(f" {C_PINK}[Target Endpoint]{RESET}       -> https://anichin.moe/az-lists/")
    print(f" {C_PINK}[Developer]{RESET}             -> Vexalyn Developer")
    print("─" * 125)

def clean_duplicated_title(title: str) -> str:
    if not title:
        return "Unknown Title"
    length = len(title)
    if length % 2 == 0:
        mid = length // 2
        if title[:mid] == title[mid:]:
            return title[:mid]
    return title

async def scrape_az_list(show_param: str, page: int):
    base_url = "https://anichin.moe/az-lists/"
    
    # Encode parameter dengan aman (misal simbol '#' otomatis jadi '%23')
    encoded_show = quote(show_param)
    query_str = f"?show={encoded_show}" if show_param else ""
    
    if page > 1:
        target_url = f"https://anichin.moe/az-lists/page/{page}/{query_str}"
    else:
        target_url = f"{base_url}{query_str}"

    t_start = time.time()
    
    def _fetch():
        try:
            r = requests.get(target_url, headers=HEADERS, timeout=12, allow_redirects=True)
            return r.text, r.status_code
        except Exception:
            return None, 500

    html_content, status_code = await asyncio.to_thread(_fetch)
    elapsed = round(time.time() - t_start, 2)
    
    response = {
        "creator": "Vexalyn Developer",
        "filter_show": show_param,
        "page": page,
        "target_url": target_url,
        "statusCode": status_code,
        "status": "success" if status_code == 200 else "error",
        "message": f"Mantap! Berhasil menarik data A-Z List filter '{show_param}' halaman {page}." if status_code == 200 else f"Gagal mengambil halaman (Status Code: {status_code})",
        "ok": status_code == 200,
        "elapsed_time": f"{elapsed} seconds",
        "total_items": 0,
        "data": []
    }

    if status_code != 200 or not html_content:
        response["message"] = f"Duh, zonk bro! Halaman untuk filter '{show_param}' tidak ditemukan (Status Code: {status_code})."
        response["ok"] = False
        return response

    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        cards = soup.select('article.bs, .listupd article.bs')
        
        items = []
        for card in cards:
            a_tag = card.select_one('a.tip, a')
            if not a_tag or not a_tag.get('href'):
                continue
                
            link = a_tag.get('href')
            if not link.startswith("http"):
                link = f"https://anichin.moe{link}" if link.startswith('/') else f"https://anichin.moe/{link}"
            
            raw_title = a_tag.get('title') or ""
            if not raw_title:
                title_el = card.select_one('.tt, h2, h3, .title, .entry-title')
                raw_title = title_el.text.strip() if title_el else "Unknown Title"
            
            title = clean_duplicated_title(raw_title)
            
            img_el = card.select_one('img')
            thumbnail = ""
            if img_el:
                thumbnail = img_el.get('data-src') or img_el.get('src') or ""

            type_el = card.select_one('.typez, .type, .lplez')
            dtype = type_el.text.strip() if type_el else "Donghua"

            status_el = card.select_one('.status')
            status_text = status_el.text.strip() if status_el else "Completed"

            sub_el = card.select_one('.bt span.sb, .sub')
            sub_text = sub_el.text.strip() if sub_el else "Sub"

            items.append({
                "title": title,
                "url": link,
                "thumbnail": thumbnail,
                "type": dtype,
                "status": status_text,
                "sub": sub_text
            })

        response["total_items"] = len(items)
        response["data"] = items

    except Exception as e:
        response["statusCode"] = 500
        response["status"] = "error"
        response["message"] = f"Waduh ada error saat parsing HTML: {str(e)}"
        response["ok"] = False

    return response

async def main():
    print_banner()
    
    print(f"\n{C_PINK}[?]{RESET} {C_BLUE}Pilih Filter A-Z List:{RESET}")
    print(f"    {C_CYAN}- # (untuk simbol){RESET}")
    print(f"    {C_CYAN}- 0-9 (untuk angka){RESET}")
    print(f"    {C_CYAN}- A - Z (untuk huruf, misal: A, B, C, dst){RESET}")
    
    show_input = input(f" {C_PURPLE}╰─ Masukkan filter show [default: A]:{RESET} ").strip()
    
    if not show_input:
        show_param = "A"
    else:
        show_param = show_input

    print(f"\n{C_PINK}[?]{RESET} {C_BLUE}Masukkan Nomor Halaman (Page):{RESET}")
    page_input = input(f" {C_PURPLE}╰─ Masukkan nomor halaman [default: 1]:{RESET} ").strip()
    
    try:
        page = int(page_input) if page_input else 1
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    print()
    await loading_animation(f"Menghubungkan ke A-Z List [Filter: {show_param}]", 0.3)
    await loading_animation(f"Mengambil data halaman ke-{page}", 0.4)
    
    print(f"\n{C_PINK}[*]{RESET} {C_BLUE}Processing A-Z payload extraction...{RESET}")
    
    start_time = time.time()
    result = await scrape_az_list(show_param, page)
    execution_time = round(time.time() - start_time, 2)
    
    print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
    print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Filter / Page:{RESET} {C_CYAN}{result['filter_show']} - Page {result['page']}{RESET}")
    print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}{result['statusCode']}{RESET}")
    print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Total Items:{RESET} {C_CYAN}{result['total_items']} items found{RESET}")
    print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Elapsed Time:{RESET} {C_CYAN}{execution_time} seconds{RESET}")
    print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
    
    print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
    print(f"{C_CYAN}{json.dumps(result, indent=4, ensure_ascii=False)}{RESET}")
    
    print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
    print(f"{C_PINK}[!] Operational complete. Vexalyn Scraper core closed safely.{RESET}\n")

if __name__ == "__main__":
    asyncio.run(main())