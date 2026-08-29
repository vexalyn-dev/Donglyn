# filter.py
import sys
import asyncio
import json
import time
import urllib.parse
import requests
from bs4 import BeautifulSoup
from core.browser import get_page_content

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://anichin.moe/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}

async def get_page_content_fast(url: str):
    """Fast path pakai requests (0.5-1s), fallback ke Playwright kalau kena CF/403."""
    def _fetch():
        try:
            r = requests.get(url, headers=HEADERS, timeout=8)
            if r.status_code == 200:
                txt = r.text
                if "Just a moment" in txt or "cf-challenge" in txt.lower() or "Attention Required" in txt:
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
        else:
            fallback_html = await get_page_content(url)
            return fallback_html, None, code if code else 200
    
    fallback_html = await get_page_content(url)
    return fallback_html, None, 200

# ANSI Colors - Tema Pink, Ungu, Biru
C_PURPLE = "\033[35m"
C_PINK = "\033[95m"
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"
C_RED = "\033[91m"
RESET = "\033[0m"

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
    print(f" {C_PINK}[Module]{RESET}                -> Clean Card Scraper (No Score, with Status & Sub)")
    print(f" {C_PINK}[Target Endpoint]{RESET}       -> https://anichin.moe/anime/?...")
    print(f" {C_PINK}[Developer]{RESET}             -> Vexalyn Developer")
    print("─" * 125)

def clean_duplicated_title(title: str) -> str:
    """Membersihkan judul anime yang double (misal: 'TitleTitle' jadi 'Title')."""
    if not title:
        return "Unknown Title"
    length = len(title)
    if length % 2 == 0:
        mid = length // 2
        if title[:mid] == title[mid:]:
            return title[:mid]
    return title

async def scrape_unified_filter(params: dict):
    query_params = []

    # 1. Page
    page_val = params.get("page", "").strip().lower()
    if page_val and page_val != "all" and page_val.isdigit():
        query_params.append(f"page={page_val}")
    else:
        page_val = "1 (Default)"

    # 2. Genre
    genre_val = params.get("genre", "").strip().lower()
    if genre_val and genre_val != "all":
        genres = [g.strip().replace(" ", "-") for g in genre_val.split(",") if g.strip()]
        for idx, g in enumerate(genres):
            query_params.append("genre%5B" + str(idx) + "%5D=" + urllib.parse.quote(g))

    # 3. Type
    type_val = params.get("type", "").strip().lower()
    if type_val and type_val != "all":
        query_params.append(f"type={urllib.parse.quote(type_val)}")

    # 4. Season
    season_val = params.get("season", "").strip().lower()
    if season_val and season_val != "all":
        seasons = [s.strip().replace(" ", "-") for s in season_val.split(",") if s.strip()]
        for idx, s in enumerate(seasons):
            query_params.append("season%5B" + str(idx) + "%5D=" + urllib.parse.quote(s))

    # 5. Sub
    sub_val = params.get("sub", "").strip().lower()
    if sub_val and sub_val != "all":
        query_params.append(f"sub={urllib.parse.quote(sub_val)}")

    # 6. Studio
    studio_val = params.get("studio", "").strip().lower()
    if studio_val and studio_val != "all":
        studio_slug = studio_val.replace(" ", "-")
        query_params.append(f"studio={urllib.parse.quote(studio_slug)}")

    # 7. Orderby
    orderby_val = params.get("orderby", "").strip().lower()
    if orderby_val and orderby_val != "all":
        query_params.append(f"order={urllib.parse.quote(orderby_val)}")

    # 8. Status
    status_val = params.get("status", "").strip().lower()
    if status_val and status_val != "all":
        query_params.append(f"status={urllib.parse.quote(status_val)}")

    target_url = "https://anichin.moe/anime/?" + "&".join(query_params) if query_params else "https://anichin.moe/anime/"

    html_content, error, fetch_code = await get_page_content_fast(target_url)
    
    response = {
        "creator": "Vexalyn Developer",
        "statusCode": fetch_code if fetch_code else 200,
        "status": "success",
        "message": "Mantap! Berhasil mengambil hasil filter data anime.",
        "ok": True,
        "data": {
            "page": page_val,
            "applied_params": params,
            "url": target_url,
            "total_items": 0,
            "results": []
        }
    }
    
    if error or fetch_code != 200 or not html_content or not isinstance(html_content, str):
        response["statusCode"] = fetch_code if fetch_code and fetch_code != 200 else 404
        response["status"] = "error"
        response["message"] = f"Duh, zonk bro! Data filter tidak ditemukan (Status Code: {response['statusCode']})."
        response["ok"] = False
        return response

    soup = BeautifulSoup(html_content, 'html.parser')
    
    try:
        items = []
        cards = soup.select('.listupd article.bs, .post-item, div.excstld, .archive-container article')
        
        if not cards:
            cards = soup.select('article.bs, .utao, div.bsx')

        for card in cards:
            a_tag = card.select_one('a')
            if not a_tag or not a_tag.get('href'):
                continue
                
            link = a_tag.get('href')
            if not link.startswith("http"):
                link = f"https://anichin.moe{link}" if link.startswith('/') else f"https://anichin.moe/{link}"
            
            title_el = card.select_one('.tt, h2, h3, .title, .entry-title')
            raw_title = title_el.text.strip() if title_el else (a_tag.get('title') or "Unknown Title")
            title = clean_duplicated_title(raw_title)
            
            img_el = card.select_one('img')
            thumbnail = ""
            if img_el:
                thumbnail = img_el.get('data-src') or img_el.get('src') or ""

            # Type (misal: Donghua)
            type_el = card.select_one('.type, .epz')
            dtype = type_el.text.strip() if type_el else "Donghua"

            # Status (misal: Ongoing / Completed)
            status_el = card.select_one('.status')
            status_text = status_el.text.strip() if status_el else "Unknown"

            # Sub / Type ket (misal: Sub / Dub / Raw)
            sub_el = card.select_one('.sub')
            sub_text = sub_el.text.strip() if sub_el else "Sub"

            items.append({
                "title": title,
                "url": link,
                "thumbnail": thumbnail,
                "type": dtype,
                "status": status_text,
                "sub": sub_text
            })

        response["data"]["total_items"] = len(items)
        response["data"]["results"] = items

    except Exception as e:
        response["statusCode"] = 500
        response["status"] = "error"
        response["message"] = f"Waduh ada error saat parsing: {str(e)}"
        response["ok"] = False

    return response

async def main():
    print_banner()
    
    print(f"\n{C_PINK}[?]{RESET} {C_BLUE}Masukkan Filter Lengkap (Atau tekan Enter untuk All semua):{RESET}")
    print(f"    {C_CYAN}Contoh: genre=action type=donghua season=spring-2026 sub=sub studio=all orderby=latest status=ongoing page=1{RESET}")
    single_input = input(f" {C_PURPLE}╰─>{RESET} ").strip()

    filter_params = {
        "genre": "all",
        "type": "all",
        "season": "all",
        "sub": "all",
        "studio": "all",
        "orderby": "all",
        "status": "all",
        "page": ""
    }

    if single_input:
        parts = single_input.split()
        for part in parts:
            if "=" in part:
                key, val = part.split("=", 1)
                key = key.strip().lower()
                val = val.strip()
                if key in filter_params:
                    filter_params[key] = val

    await loading_animation("Menghubungkan ke query filter Anichin", 0.4)
    await loading_animation("Mem-parsing hasil data filter", 0.6)
    
    print(f"\n{C_PINK}[*]{RESET} {C_BLUE}Processing payload hook onto target DOM structure...{RESET}")
    
    start_time = time.time()
    result = await scrape_unified_filter(filter_params)
    execution_time = round(time.time() - start_time, 2)
    
    print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
    sc_val = result['statusCode']
    total_val = result['data']['total_items']
    
    print(C_PINK + "[SUCCESS]" + RESET + " " + C_BLUE + "Status Code:" + RESET + " " + C_CYAN + str(sc_val) + RESET)
    print(C_PINK + "[SUCCESS]" + RESET + " " + C_BLUE + "Total Found:" + RESET + " " + C_CYAN + str(total_val) + " items" + RESET)
    print(C_PINK + "[SUCCESS]" + RESET + " " + C_BLUE + "Elapsed Time:" + RESET + " " + C_CYAN + str(execution_time) + " seconds" + RESET)
    print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
    
    print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
    print(f"{C_CYAN}{json.dumps(result, indent=4, ensure_ascii=False)}{RESET}")
    
    print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
    print(f"{C_PINK}[!] Operational complete. Vexalyn Scraper core closed safely.{RESET}\n")

if __name__ == "__main__":
    asyncio.run(main())