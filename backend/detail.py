# detail.py
import sys
import asyncio
import json
import time
import urllib.parse
import re
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
                # deteksi Cloudflare challenge
                if "Just a moment" in txt or "cf-challenge" in txt.lower() or "Attention Required" in txt:
                    return None, 403
                return txt, 200
            return None, r.status_code
        except Exception:
            return None, 500
    
    html, code = await asyncio.to_thread(_fetch)
    if html:
        return html, None, code
    # fallback lambat
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
                                                 
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 [Module]                -> Detail Scraper (Precise div.bixbox.synp Parser)
 [Target Endpoint]       -> https://anichin.moe
 [Developer]             -> Vexalyn Developer
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────"""
    print(f"{C_PURPLE}{banner}{RESET}")

async def resolve_target_url(query: str):
    clean_query = query.strip()
    if clean_query.startswith("http"):
        return clean_query, 200
        
    if " " not in clean_query and not clean_query.isnumeric():
        return f"https://anichin.moe/{clean_query.lower().strip('/')}/", 200

    encoded_query = urllib.parse.quote(clean_query)
    search_url = f"https://anichin.moe/?s={encoded_query}"
    
    html_content, error, code = await asyncio.to_thread(lambda: (lambda r: (r.text if r.status_code == 200 else None, None, r.status_code))(requests.get(search_url, headers=HEADERS, timeout=8)))
    if error or not html_content:
        return None, code

    soup = BeautifulSoup(html_content, 'html.parser')
    first_item = soup.select_one('div.utao a, article.bs a, div.bsx a, .kanan h2 a, .film-list li a')
    if first_item and first_item.get('href'):
        main_url = first_item.get('href')
        if not main_url.startswith("http"):
            main_url = f"https://anichin.moe{main_url}" if main_url.startswith('/') else f"https://anichin.moe/{main_url}"
        return main_url, 200
        
    return None, 404

async def scrape_detail(user_input: str):
    target_url, resolve_code = await resolve_target_url(user_input)
    
    if not target_url:
        return {
            "creator": "Vexalyn Developer",
            "statusCode": resolve_code if resolve_code != 200 else 404,
            "status": "error",
            "message": f"Donghua dengan keyword '{user_input}' tidak ditemukan di Anichin.",
            "ok": False,
            "data": {}
        }

    html_content, error, fetch_code = await get_page_content_fast(target_url)
    
    response = {
        "creator": "Vexalyn Developer",
        "statusCode": fetch_code,
        "status": "success",
        "message": f"Successfully fetched target: '{target_url}'",
        "ok": True,
        "data": {}
    }
    
    if error or fetch_code != 200:
        response["statusCode"] = fetch_code if fetch_code != 200 else 500
        response["status"] = "error"
        response["message"] = f"Failed to load page with status code: {response['statusCode']}"
        response["ok"] = False
        return response

    soup = BeautifulSoup(html_content, 'html.parser')
    
    try:
        # 1. Judul Utama
        title_el = soup.select_one('h2[itemprop="partOfSeries"], .infolimit h2, .infox h2, h1.entry-title, .post-title h1, h1')
        title = title_el.text.strip() if title_el else "Unknown Title"
        title = re.sub(r'\s*Episode\s+\d+.*$', '', title, flags=re.IGNORECASE).strip()

        # 2. Rating
        rating_val = "N/A"
        rt_div = soup.select_one('.rating strong, .rt strong, [itemprop="ratingValue"], .rating, .numval')
        if rt_div:
            raw_rt = rt_div.get_text(' ', strip=True)
            match_rt = re.search(r'(\d+\.\d+|\d+)', raw_rt)
            if match_rt:
                rating_val = match_rt.group(1)
        if rating_val == "N/A":
            rtb = soup.select_one('.rtb span')
            if rtb and rtb.get('style'):
                m = re.search(r'width:\s*([0-9.]+)%', rtb.get('style'))
                if m:
                    try: rating_val = str(round(float(m.group(1))/10, 2))
                    except: pass

        # 3. Thumbnail Poster
        poster_img = soup.select_one('.thumb img, .bigcontent .thumb img, .infox .thumb img, .fotoimg img')
        thumbnail = (poster_img.get('data-src') or poster_img.get('src')) if poster_img else "No Thumbnail"

        # 4. Genre List
        genres = []
        genre_tags = soup.select('div.genxed a[rel="tag"], div.genxed a[href*="/genres/"], .genx a[href*="/genres/"]')
        for tag in genre_tags:
            g_text = tag.text.strip()
            if g_text and g_text not in genres:
                genres.append(g_text)
        if not genres:
            for tag in soup.select('div.genx a'):
                g_text = tag.text.strip()
                if g_text and g_text not in genres:
                    genres.append(g_text)

        # 5. Metadata
        metadata = {
            "status": "N/A",
            "studio": "N/A",
            "duration": "N/A",
            "country": "N/A",
            "episodes": "N/A",
            "network": "N/A",
            "release_date": "N/A",
            "season": "N/A",
            "type": "N/A",
            "subber": "N/A"
        }
        info_items = soup.select('.info-content .spe span, .infox .spe span')
        for item in info_items:
            text = item.get_text(' ', strip=True)
            if ":" in text:
                key, val = text.split(":", 1)
                key_clean = key.strip().lower()
                val_clean = val.strip()
                if "status" in key_clean: metadata["status"] = val_clean
                elif "studio" in key_clean: metadata["studio"] = val_clean
                elif "durasi" in key_clean: metadata["duration"] = val_clean
                elif "negara" in key_clean: metadata["country"] = val_clean
                elif "episode" in key_clean: metadata["episodes"] = val_clean
                elif "network" in key_clean: metadata["network"] = val_clean
                elif "tanggal rilis" in key_clean or "rilis" in key_clean: metadata["release_date"] = val_clean
                elif "season" in key_clean: metadata["season"] = val_clean
                elif "tipe" in key_clean: metadata["type"] = val_clean
                elif "subber" in key_clean: metadata["subber"] = val_clean

        # 6. Sinopsis
        SPAM_MARKERS = ["Download", "Nonton", "jangan lupa mengklik tombol like", "Mirrored", "PixelDrain", "Terabox", "360p", "480p", "1080p"]
        synopsis = "No Synopsis Available"
        for sel in ['.desc.mindes', '.desc', '.synopsis', '.synp', '[itemprop="description"]']:
            el = soup.select_one(sel)
            if not el: continue
            txt = el.get_text(' ', strip=True)
            if any(m.lower() in txt.lower() for m in SPAM_MARKERS) and len(txt) > 200:
                continue
            if len(txt) < 40:
                continue
            for _ in range(3):
                low = txt.lower()
                if low.startswith("sinopsis"):
                    txt = txt[8:].lstrip(' :–—-').strip()
                    continue
                if low.startswith(title.lower()):
                    txt = txt[len(title):].lstrip(' :–—-.').strip()
                    continue
                break
            synopsis = txt.strip()
            break
        if synopsis == "No Synopsis Available":
            for sel in ['div.bixbox.synp div.entry-content p', 'div.entry-content']:
                el = soup.select_one(sel)
                if not el: continue
                txt = el.get_text(' ', strip=True)
                if any(m.lower() in txt.lower() for m in SPAM_MARKERS) and len(txt) > 200:
                    continue
                if len(txt) > 40:
                    for _ in range(3):
                        low = txt.lower()
                        if low.startswith("sinopsis"):
                            txt = txt[8:].lstrip(' :–—-').strip()
                            continue
                        if low.startswith(title.lower()):
                            txt = txt[len(title):].lstrip(' :–—-.').strip()
                            continue
                        break
                    synopsis = txt.strip()
                    break

        response["data"] = {
            "title": title,
            "url": target_url,
            "rating": rating_val,
            "thumbnail": thumbnail,
            "genres": genres,
            **metadata,
            "synopsis": synopsis
        }

    except Exception as e:
        response["statusCode"] = 500
        response["status"] = "error"
        response["message"] = f"Parsing error: {str(e)}"
        response["ok"] = False

    return response

async def main():
    print_banner()
    
    print(f"{C_PINK}[?]{RESET} {C_BLUE}Masukkan Judul / Slug / URL Donghua:{RESET}")
    user_input = input(f" {C_PURPLE}╰─>{RESET} ").strip()
    
    if not user_input:
        print(f"{C_RED}[!] Input tidak boleh kosong.{RESET}")
        return

    await loading_animation("Menyelesaikan Target URL (Resolver)", 0.3)
    await loading_animation("Mengambil metadata, genre, & sinopsis presisi", 0.5)
    
    print(f"\n{C_PINK}[*]{RESET} {C_BLUE}Processing payload hook onto target DOM structure...{RESET}")
    
    start_time = time.time()
    result = await scrape_detail(user_input)
    execution_time = round(time.time() - start_time, 2)
    
    print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
    if result["ok"]:
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}{result['statusCode']}{RESET}")
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Title Found:{RESET} {C_CYAN}{result['data']['title']}{RESET}")
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Resolved URL:{RESET} {C_CYAN}{result['data']['url']}{RESET}")
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