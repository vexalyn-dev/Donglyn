# search.py
import sys
import asyncio
import json
import time
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
from core.browser import get_page_content

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://anichin.moe/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

async def get_page_content_fast(url: str):
    def _fetch():
        try:
            r = requests.get(url, headers=HEADERS, timeout=8)
            return r.text, r.status_code
        except requests.exceptions.Timeout:
            return None, 504
        except requests.exceptions.ConnectionError:
            return None, 503
        except Exception:
            return None, 500
            
    html, status_code = await asyncio.to_thread(_fetch)
    if html and status_code == 200 and "Just a moment" not in html and "cf-challenge" not in html.lower():
        return html, 200
    if html and ("Just a moment" in html or "cf-challenge" in html.lower()):
        return None, 403
    
    # Kalau fast fetch gagal, lempar ke browser handler
    browser_html = await get_page_content(url)
    if browser_html:
        return browser_html, 200
    return None, status_code if isinstance(status_code, int) else 500

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
 [Module]                -> Search Scraper (search.py)
 [Target Endpoint]       -> https://anichin.moe
 [Developer]             -> Vexalyn Developer
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────"""
    print(f"{C_PURPLE}{banner}{RESET}")

async def scrape_search(query: str):
    # Cek Validasi Input (400 Bad Request kalau kosong)
    if not query or not query.strip():
        return {
            "creator": "Vexalyn Developer",
            "statusCode": 400,
            "status": "error",
            "message": "Waduh, kata kunci pencariannya jangan dikosongin dong bos!",
            "ok": False,
            "total_data": 0,
            "data": []
        }

    encoded_query = urllib.parse.quote(query.strip())
    url = f"https://anichin.moe/?s={encoded_query}"
    
    html_content, status_code = await get_page_content_fast(url)
    
    # Mapping status error HTTP dengan bahasa casual
    if not html_content or status_code != 200:
        err_code = status_code if isinstance(status_code, int) else 500
        
        if err_code == 403:
            err_msg = "Yah, diblokir Cloudflare target nih. Coba lagi nanti atau ganti jaringan."
        elif err_code == 404:
            err_msg = "Waduh, halaman pencarian gak ketemu di server."
        elif err_code == 503:
            err_msg = "Duh, server Anichin-nya lagi ngambek atau down tuh."
        elif err_code == 504:
            err_msg = "Koneksi nyangkut alias timeout, kelamaan nunggu balasan dari server target."
        else:
            err_msg = f"Gagal narik halaman pencarian, server merespon dengan status code {err_code}."

        return {
            "creator": "Vexalyn Developer",
            "statusCode": err_code,
            "status": "error",
            "message": err_msg,
            "ok": False,
            "total_data": 0,
            "data": []
        }

    soup = BeautifulSoup(html_content, 'html.parser')
    extracted_data = []
    seen_urls = set()
    
    items = soup.select('div.utao, article.bs, div.bsx, .kanan, .film-list li')
    
    for item in items:
        try:
            a_tag = item.find('a')
            if not a_tag: continue
            
            link = a_tag.get('href')
            if not link: continue
            
            if not link.startswith('http'):
                link = f"https://anichin.moe{link}" if link.startswith('/') else f"https://anichin.moe/{link}"
            
            if link in seen_urls:
                continue
            seen_urls.add(link)

            # Judul — bersihkan dobel Episode/Subtitle + dobel string
            title_el = item.select_one('h2, .title, .tt, .entry-title')
            raw_title = (a_tag.get('title') or "").strip()
            if not raw_title and title_el:
                raw_title = title_el.get_text(strip=True)
            if not raw_title:
                raw_title = a_tag.get_text(strip=True)
            if not raw_title: continue
            clean_title = re.sub(r'\s*Episode\s+\d+.*$', '', raw_title, flags=re.IGNORECASE).strip()
            clean_title = re.sub(r'\s*Subtitle\s+Indonesia.*$', '', clean_title, flags=re.IGNORECASE).strip()
            half = len(clean_title)//2
            if len(clean_title)%2==0 and half>5 and clean_title[:half]==clean_title[half:]:
                title = clean_title[:half]
            else:
                title = clean_title or "Tanpa Judul"

            # Thumbnail — prioritas data-src (lazy) baru src/srcset
            img_tag = item.find('img')
            thumb = ""
            if img_tag:
                thumb = img_tag.get('data-src') or img_tag.get('src') or ""
                if not thumb and img_tag.get('srcset'):
                    thumb = img_tag.get('srcset').split(',')[0].split()[0]
            if not thumb: thumb = "No Thumbnail"
            
            # Status/Type/Label — pakai logic konsisten
            card_text = item.get_text(' ', strip=True).lower()
            status_el = item.select_one('.epx, .bt .ep, .score, .status')
            status = status_el.get_text(strip=True) if status_el else ""
            if not status or status.lower() in ["ongoing","completed","tamat","hiatus","sub","dub","n/a"]:
                for el in item.select('span, div'):
                    txt = el.get_text(strip=True)
                    if txt and txt.lower() not in ["ongoing","completed","tamat","hiatus","sub","dub"]:
                        if re.match(r'^(Ep\s*)?\d+', txt, re.I) or txt.lower().startswith('ep'):
                            status = txt; break
            if not status or status.lower() in ["ongoing","completed"]:
                if "completed" in card_text or "tamat" in card_text: status = "Completed"
                elif "hiatus" in card_text: status = "Hiatus"
                elif status in ["ongoing","completed"]: pass
                else: status = "Ongoing" if not status else status
            
            type_el = item.select_one('.typez, .type, span.type')
            anime_type = type_el.get_text(strip=True) if type_el else ("Anime" if "anime" in card_text and "donghua" not in card_text else "Donghua")
            if anime_type not in ["Donghua","Anime"]: anime_type = "Donghua" if "donghua" in card_text else "Anime" if "anime" in card_text else "Donghua"
            
            sub_el = item.select_one('.sb, span.sub, .sub, .term')
            sub = sub_el.get_text(strip=True) if sub_el else ("Dub" if "dub" in card_text else "Sub")
            if sub not in ["Sub","Dub"] and "dub" in sub.lower(): sub="Dub"
            elif sub not in ["Sub","Dub"]: sub="Sub"
            
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
            
    total_data = len(extracted_data)
    
    # Kalau hasil pencarian kosong (404 Not Found)
    if total_data == 0:
        return {
            "creator": "Vexalyn Developer",
            "statusCode": 404,
            "status": "error",
            "message": f"Duh, Zonk bro! Gak ada hasil pencarian buat kata kunci '{query}'.",
            "ok": False,
            "total_data": 0,
            "data": []
        }

    return {
        "creator": "Vexalyn Developer",
        "statusCode": 200,
        "status": "success",
        "message": f"Mantap! Berhasil nyomot hasil pencarian buat: '{query}'",
        "ok": True,
        "total_data": total_data,
        "data": extracted_data
    }

async def main():
    print_banner()
    
    print(f"{C_PINK}[?]{RESET} {C_BLUE}Masukkan judul donghua yang mau dicari:{RESET}")
    search_query = input(f" {C_PURPLE}╰─>{RESET} ").strip()
    
    if not search_query:
        print(f"\n{C_RED}[CRITICAL ERROR]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}400{RESET}")
        print(f"{C_RED}[REASON]{RESET} {C_CYAN}Waduh, query pencariannya jangan dikosongin dong!{RESET}")
        return

    await loading_animation("Membangun koneksi ke Anichin", 0.5)
    await loading_animation(f"Lagi nyari data buat '{search_query}'", 0.5)
    
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
        print(f"{C_RED}[ERROR RESPONSE]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}{result['statusCode']}{RESET}")
        print(f"{C_RED}[REASON]{RESET} {C_CYAN}{result['message']}{RESET}")
        print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
        print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
        print(f"{C_RED}{json.dumps(result, indent=4, ensure_ascii=False)}{RESET}")
    
    print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
    print(f"{C_PINK}[!] Operational complete. Vexalyn Scraper core closed safely.{RESET}\n")

if __name__ == "__main__":
    asyncio.run(main())