# search.py
import sys
import asyncio
import json
import time
import urllib.parse
from bs4 import BeautifulSoup
from core.browser import get_page_content

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
8888888b.   .d88888b.  888b    888  .d8888b.  888    888 888     888      d8888       .d8888b.   .d8888b.  8888888b.         d8888 8888888b.  8888888888 8888888b.  
888  "Y88b d88P" "Y88b 8888b   888 d88P  Y88b 888    888 888     888     d88888      d88P  Y88b d88P  Y88b 888   Y88b       d88888 888   Y88b 888        888   Y88b 
888    888 888     888 88888b  888 888    888 888    888 888     888    d88P888      Y88b.      888    888 888    888      d88P888 888    888 888        888    888 
888    888 888     888 888Y88b 888 888        8888888888 888     888   d88P 888       "Y888b.   888        888   d88P     d88P 888 888   d88P 8888888    888   d88P 
888    888 888     888 888 Y88b888 888  88888 888    888 888     888  d88P  888          "Y88b. 888        8888888P"     d88P  888 8888888P"  888        8888888P"  
888    888 888     888 888  Y88888 888    888 888    888 888     888 d88P   888            "888 888    888 888 T88b     d88P   888 888        888        888 T88b   
888  .d88P Y88b. .d88P 888   Y8888 Y88b  d88P 888    888 Y88b. .d88P d8888888888      Y88b  d88P Y88b  d88P 888  T88b   d8888888888 888        888        888  T88b  
8888888P"   "Y88888P"  888    Y888  "Y8888P88 888    888  "Y88888P" d88P     888       "Y8888P"   "Y8888P"  888   T88b d88P     888 888        8888888888 888   T88b 
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 [Module]                -> Search Scraper (search.py)
 [Target Endpoint]       -> https://anichin.moe
 [Developer]             -> Vexalyn Developer
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────"""
    print(f"{C_PURPLE}{banner}{RESET}")

async def scrape_search(query: str):
    encoded_query = urllib.parse.quote(query)
    url = f"https://anichin.moe/?s={encoded_query}"
    
    html_content, error = await get_page_content(url)
    
    response = {
        "creator": "Vexalyn Developer",
        "statusCode": 200,
        "status": "success",
        "message": f"Successfully fetched search results for: '{query}'",
        "ok": True,
        "total_data": 0,
        "data": []
    }
    
    if error:
        response["statusCode"] = 500
        response["status"] = "error"
        response["message"] = f"Failed to load search page: {error}"
        response["ok"] = False
        return response

    soup = BeautifulSoup(html_content, 'html.parser')
    extracted_data = []
    seen_urls = set() # Filter anti-duplikat
    
    items = soup.select('div.utao, article.bs, div.bsx')
    
    for item in items:
        try:
            a_tag = item.find('a')
            if not a_tag: continue
            
            # --- FIX URL ---
            link = a_tag.get('href')
            if not link: continue
            
            # Tambahkan domain anichin.moe kalau url-nya relative
            if not link.startswith('http'):
                link = f"https://anichin.moe{link}" if link.startswith('/') else f"https://anichin.moe/{link}"
            
            # Skip kalau link ini udah diproses (Anti Duplikat)
            if link in seen_urls:
                continue
            seen_urls.add(link)

            # --- FIX JUDUL ---
            title = a_tag.get('title')
            if not title:
                title_el = item.find(['h2', 'div'], class_=lambda c: c and 'tt' in c)
                title = title_el.text.strip() if title_el else None
            
            if not title: continue

            # --- FIX THUMBNAIL ---
            img_tag = item.find('img')
            thumb = img_tag.get('data-src') or img_tag.get('src') if img_tag else "No Thumbnail"
            
            # --- FIX LABEL / BADGES (Sesuai gambar web target) ---
            status_el = item.find(['div', 'span'], class_=lambda c: c and ('epx' in c or 'status' in c))
            status = status_el.text.strip() if status_el else "N/A"
            
            type_el = item.find(['div', 'span'], class_=lambda c: c and 'typez' in c)
            anime_type = type_el.text.strip() if type_el else "N/A"
            
            sub_el = item.find(['div', 'span'], class_=lambda c: c and ('sb' in c or 'sub' in c))
            sub = sub_el.text.strip() if sub_el else "N/A"
            
            extracted_data.append({
                "title": title,
                "url": link,
                "status": status,
                "type": anime_type,
                "label": sub,
                "thumbnail": thumb
            })
        except Exception:
            continue
            
    response["total_data"] = len(extracted_data)
    response["data"] = extracted_data
    
    if response["total_data"] == 0:
        response["message"] = "0 Data ditemukan. Pastikan kata kunci benar atau cek struktur web."

    return response

async def main():
    print_banner()
    
    print(f"{C_PINK}[?]{RESET} {C_BLUE}Masukkan judul donghua yang mau dicari:{RESET}")
    search_query = input(f" {C_PURPLE}╰─>{RESET} ").strip()
    
    if not search_query:
        print(f"{C_RED}[!] Query tidak boleh kosong.{RESET}")
        return

    await loading_animation("Membangun koneksi ke Anichin", 0.5)
    await loading_animation(f"Mencari data untuk '{search_query}'", 0.5)
    
    print(f"\n{C_PINK}[*]{RESET} {C_BLUE}Processing payload hook onto target DOM structure...{RESET}")
    
    start_time = time.time()
    result = await scrape_search(search_query)
    execution_time = round(time.time() - start_time, 2)
    
    print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
    if result["ok"]:
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}{result['statusCode']}{RESET}")
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Payload Size:{RESET} {C_CYAN}{result['total_data']} items extracted{RESET}")
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Elapsed Time:{RESET} {C_CYAN}{execution_time} seconds{RESET}")
        print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
        
        print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
        print(f"{C_CYAN}{json.dumps(result, indent=4, ensure_ascii=False)}{RESET}")
    else:
        print(f"{C_RED}[CRITICAL ERROR]{RESET} {C_BLUE}Execution aborted.{RESET}")
        print(f"{C_RED}[REASON]{RESET} {C_CYAN}{result['message']}{RESET}")
    
    print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
    print(f"{C_PINK}[!] Operational complete. Vexalyn Scraper core closed safely.{RESET}\n")

if __name__ == "__main__":
    asyncio.run(main())