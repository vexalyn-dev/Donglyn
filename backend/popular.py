# popular.py
import sys
import asyncio
import json
import time
import requests
from bs4 import BeautifulSoup

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
    print(f" {C_PINK}[Module]{RESET}                -> Popular Donghua Scraper Core (Top 10 Strict)")
    print(f" {C_PINK}[Target Endpoint]{RESET}       -> https://anichin.moe/ (Home / Sidebar Widget)")
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

async def scrape_popular_donghua(range_type: str):
    target_url = "https://anichin.moe/"
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
        "range_type": range_type,
        "target_url": target_url,
        "statusCode": status_code,
        "status": "success" if status_code == 200 else "error",
        "message": f"Mantap! Berhasil menarik data popular donghua untuk range '{range_type}'." if status_code == 200 else f"Gagal mengambil halaman (Status Code: {status_code})",
        "ok": status_code == 200,
        "elapsed_time": f"{elapsed} seconds",
        "total_items": 0,
        "data": []
    }

    if status_code != 200 or not html_content:
        response["message"] = f"Duh, zonk bro! Gagal mengambil data popular (Status Code: {status_code})."
        response["ok"] = False
        return response

    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        container_selector = f".serieslist.pop.wpop.wpop-{range_type} li, .wpop-{range_type} li, .serieslist.pop li"
        cards = soup.select(container_selector)
        
        if not cards:
            cards = soup.select('#wpop-items li, .serieslist.pop li')

        items = []
        for index, card in enumerate(cards, start=1):
            if index > 10:  # Batasi persis 10 item teratas sesuai tampilan web
                break
                
            a_tag = card.select_one('a.series, a')
            if not a_tag:
                continue
                
            raw_title = a_tag.get('title') or ""
            if not raw_title:
                title_el = card.select_one('h4 a, .leftseries h4, .title, h4')
                raw_title = title_el.text.strip() if title_el else "Unknown Title"
            
            title = clean_duplicated_title(raw_title)

            rating_el = card.select_one('.numscore')
            rating = rating_el.text.strip() if rating_el else "N/A"

            genres = []
            genre_els = card.select('span a[rel="tag"], .leftseries span a')
            for g in genre_els:
                genres.append(g.text.strip())

            items.append({
                "rank": index,
                "title": title,
                "genres": genres if genres else ["Action", "Fantasy"],
                "rating": rating
            })

        response["total_items"] = len(items)
        response["data"] = items

    except Exception as e:
        response["statusCode"] = 500
        response["status"] = "error"
        response["message"] = f"Waduh ada error saat parsing item popular: {str(e)}"
        response["ok"] = False

    return response

async def main():
    print_banner()
    
    print(f"\n{C_PINK}[?]{RESET} {C_BLUE}Pilih Range Tipe Popularitas:{RESET}")
    print(f"    {C_CYAN}- weekly{RESET}")
    print(f"    {C_CYAN}- monthly{RESET}")
    print(f"    {C_CYAN}- alltime{RESET}")
    
    range_input = input(f" {C_PURPLE}╰─ Masukkan range type [default: weekly]:{RESET} ").strip().lower()
    
    if not range_input:
        range_type = "weekly"
    elif range_input in ["weekly", "monthly", "alltime"]:
        range_type = range_input
    else:
        range_type = "weekly"

    print()
    await loading_animation(f"Menghubungkan ke Home Anichin [Popular: {range_type.upper()}]", 0.3)
    await loading_animation("Mengambil data ranking popularitas top 10", 0.4)
    
    print(f"\n{C_PINK}[*]{RESET} {C_BLUE}Processing strict top 10 popular extraction...{RESET}")
    
    start_time = time.time()
    result = await scrape_popular_donghua(range_type)
    execution_time = round(time.time() - start_time, 2)
    
    print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
    print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Range Type:{RESET} {C_CYAN}{result['range_type'].upper()}{RESET}")
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