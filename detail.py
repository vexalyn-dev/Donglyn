# detail.py
import sys
import asyncio
import json
import time
import urllib.parse
import re
from bs4 import BeautifulSoup
from core.browser import get_page_content

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
8888888b.   .d88888b.  888b    888  .d8888b.  888    888 888     888      d8888       .d8888b.   .d8888b.  8888888b.         d8888 8888888b.  8888888888 8888888b.  
888  "Y88b d88P" "Y88b 8888b   888 d88P  Y88b 888    888 888     888     d88888      d88P  Y88b d88P  Y88b 888   Y88b       d88888 888   Y88b 888        888   Y88b 
888    888 888     888 88888b  888 888    888 888    888 888     888    d88P888      Y88b.      888    888 888    888      d88P888 888    888 888        888    888 
888    888 888     888 888Y88b 888 888        8888888888 888     888   d88P 888       "Y888b.   888        888   d88P     d88P 888 888   d88P 8888888    888   d88P 
888    888 888     888 888 Y88b888 888  88888 888    888 888     888  d88P  888          "Y88b. 888        8888888P"     d88P  888 8888888P"  888        8888888P"  
888    888 888     888 888  Y88888 888    888 888    888 888     888 d88P   888            "888 888    888 888 T88b     d88P   888 888        888        888 T88b   
888  .d88P Y88b. .d88P 888   Y8888 Y88b  d88P 888    888 Y88b. .d88P d8888888888      Y88b  d88P Y88b  d88P 888  T88b   d8888888888 888        888        888  T88b  
8888888P"   "Y88888P"  888    Y888  "Y8888P88 888    888  "Y88888P" d88P     888       "Y8888P"   "Y8888P"  888   T88b d88P     888 888        8888888888 888   T88b 
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 [Module]                -> Detail Scraper (Precise div.bixbox.synp Parser)
 [Target Endpoint]       -> https://anichin.moe
 [Developer]             -> Vexalyn Developer
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────"""
    print(f"{C_PURPLE}{banner}{RESET}")

async def resolve_target_url(query: str):
    clean_query = query.strip()
    if clean_query.startswith("http"):
        return clean_query
        
    if " " not in clean_query and not clean_query.isnumeric():
        return f"https://anichin.moe/{clean_query.lower().strip('/')}/"

    encoded_query = urllib.parse.quote(clean_query)
    search_url = f"https://anichin.moe/?s={encoded_query}"
    
    html_content, error = await get_page_content(search_url)
    if error:
        return None

    soup = BeautifulSoup(html_content, 'html.parser')
    first_item = soup.select_one('div.utao a, article.bs a, div.bsx a, .kanan h2 a, .film-list li a')
    if first_item and first_item.get('href'):
        main_url = first_item.get('href')
        if not main_url.startswith("http"):
            main_url = f"https://anichin.moe{main_url}" if main_url.startswith('/') else f"https://anichin.moe/{main_url}"
        return main_url
        
    return None

async def scrape_detail(user_input: str):
    target_url = await resolve_target_url(user_input)
    
    if not target_url:
        return {
            "creator": "Vexalyn Developer",
            "statusCode": 404,
            "status": "error",
            "message": f"Donghua dengan keyword '{user_input}' tidak ditemukan di Anichin.",
            "ok": False,
            "data": {}
        }

    html_content, error = await get_page_content(target_url)
    
    response = {
        "creator": "Vexalyn Developer",
        "statusCode": 200,
        "status": "success",
        "message": f"Successfully fetched target: '{target_url}'",
        "ok": True,
        "data": {}
    }
    
    if error:
        response["statusCode"] = 500
        response["status"] = "error"
        response["message"] = f"Failed to load page: {error}"
        response["ok"] = False
        return response

    soup = BeautifulSoup(html_content, 'html.parser')
    
    try:
        # 1. Judul Utama
        title_el = soup.select_one('h1.entry-title, .post-title h1, h1')
        title = title_el.text.strip() if title_el else "Unknown Title"

        # 2. Rating
        rating_val = "N/A"
        rt_div = soup.select_one('.rt, .rating, [itemprop="ratingValue"], .numval')
        if rt_div:
            raw_rt = rt_div.text.strip()
            match_rt = re.search(r'\d+\.\d+|\d+', raw_rt)
            if match_rt:
                rating_val = match_rt.group()

        # 3. Thumbnail Poster
        poster_img = soup.select_one('.thumb img, .infox .thumb img, .fotoimg img')
        thumbnail = poster_img.get('data-src') or poster_img.get('src') if poster_img else "No Thumbnail"

        # 4. Genre List (div.genxed a)
        genres = []
        genre_tags = soup.select('div.genxed a, .genx a')
        for tag in genre_tags:
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

        info_items = soup.select('.info-content span, .spe span, .ts-infox .inex span, .alter, .infox p')
        for item in info_items:
            text = item.text.strip()
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

        # 6. Sinopsis Presisi -> Sesuai Inspect: div.bixbox.synp div.entry-content p
        synopsis = "No Synopsis Available"
        synp_p = soup.select_one('div.bixbox.synp div.entry-content p, div.synp div.entry-content p')
        if synp_p:
            synopsis = synp_p.text.strip()
        else:
            # Fallback jika div.synp tidak ketemu
            desc_alt = soup.select_one('div.entry-content[itemprop="description"] p')
            if desc_alt:
                synopsis = desc_alt.text.strip()

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