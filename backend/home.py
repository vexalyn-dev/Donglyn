# home.py
import sys
import asyncio
import json
import time
import re
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
    "Referer": "https://anichin.moe/"
}

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
 [Module]                -> Home Page Sections Scraper Core (home.py)
 [Target Endpoint]       -> https://anichin.moe/
 [Developer]             -> Vexalyn Developer
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────"""
    print(f"{C_PURPLE}{banner}{RESET}")

def parse_anime_items(container_soup):
    items = container_soup.select('div.utao, article.bs, div.bsx, .kanan, .film-list li, .excstl')
    anime_list = []
    
    for item in items:
        a_tag = item.select_one('a')
        img_tag = item.select_one('img')
        title_tag = item.select_one('h2, .title, .tt, .entry-title')
        
        if a_tag and a_tag.get('href'):
            url = a_tag.get('href')
            if not url.startswith("http"):
                url = f"https://anichin.moe{url}" if url.startswith('/') else f"https://anichin.moe/{url}"
            
            raw_title = title_tag.text.strip() if title_tag else (a_tag.get('title') or "")
            if not raw_title and a_tag.get('title'):
                raw_title = a_tag.get('title')
            
            # --- PEMBERSIHAN JUDUL DOBEL ---
            clean_title = re.sub(r'\s*Episode\s+\d+.*$', '', raw_title, flags=re.IGNORECASE).strip()
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
            
            # --- EKSTRAKSI EPISODE YANG KETAT & AMAN DARI STATUS ---
            ep_elem = item.select_one('.epx, .bt .ep, .score')
            episode = ""
            if ep_elem:
                episode = ep_elem.text.strip()
            else:
                for el in item.select('span, div'):
                    txt = el.text.strip()
                    if txt.lower() not in ["ongoing", "completed", "tamat", "hiatus", "sub", "dub"]:
                        if txt.lower().startswith('ep') or re.match(r'^(Ep\s*)?\d+', txt, re.IGNORECASE):
                            episode = txt
                            break
            
            if not episode or episode.lower() in ["ongoing", "completed", "tamat", "hiatus"]:
                url_match = re.search(r'episode-(\d+|[a-z0-9-]+)', url)
                if url_match:
                    ep_slug = url_match.group(1).replace('-', ' ')
                    if ep_slug.isdigit():
                        episode = f"Ep {ep_slug}"
                    else:
                        episode = ep_slug.title()
                else:
                    episode = "Movie" if "movie" in url else "Unknown"

            card_text = item.text.lower()
            
            # Ekstraksi Status
            status_val = "Ongoing"
            if "completed" in card_text or "tamat" in card_text or "end" in card_text:
                status_val = "Completed"
            elif "hiatus" in card_text:
                status_val = "Hiatus"

            # Ekstraksi Type
            type_val = "Donghua"
            if "anime" in card_text and "donghua" not in card_text:
                type_val = "Anime"

            # Ekstraksi Label (Sub/Dub)
            label_val = "Sub"
            label_elem = item.select_one('.sub, span.sub, .term')
            if label_elem:
                lbl_text = label_elem.text.strip()
                if lbl_text:
                    label_val = lbl_text
            elif "dub" in card_text:
                label_val = "Dub"

            anime_item = {
                "title": title,
                "url": url,
                "thumbnail": thumbnail,
                "episode": episode,
                "type": type_val,
                "label": label_val,
                "status": status_val
            }
            
            if anime_item not in anime_list:
                anime_list.append(anime_item)
                
    return anime_list

async def scrape_homepage():
    target_url = "https://anichin.moe/"
    t_start = time.time()
    
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
    elapsed = round(time.time() - t_start, 2)
    
    if not html_content or status_code != 200:
        err_code = status_code if isinstance(status_code, int) else 500
        
        if err_code == 403 or (html_content and ("Just a moment" in html_content or "cf-challenge" in html_content.lower())):
            err_code = 403
            err_msg = "Yah, diblokir Cloudflare target nih. Coba lagi nanti atau ganti jaringan."
        elif err_code == 404:
            err_msg = "Waduh, halaman beranda Anichin gak ketemu di server."
        elif err_code == 503:
            err_msg = "Duh, server Anichin-nya lagi ngambek atau down tuh."
        elif err_code == 504:
            err_msg = "Koneksi nyangkut alias timeout, kelamaan nunggu balasan dari server target."
        else:
            err_msg = f"Gagal narik beranda, server merespon dengan status code {err_code}."

        return {
            "creator": "Vexalyn Developer",
            "statusCode": err_code,
            "status": "error",
            "message": err_msg,
            "elapsed_time": f"{elapsed} seconds",
            "sections": []
        }

    soup = BeautifulSoup(html_content, 'html.parser')
    sections = []
    
    block_elements = soup.select('.releases, .section, .widget, .bixbox, div[class*="venz"], div[class*="listupd"]')
    
    for block in block_elements:
        header_tag = block.select_one('h2, h3, h4, .hport span, .releases h2, .widget-title')
        if header_tag:
            section_title = header_tag.text.strip()
            
            # --- FILTER UNTUK MEMBUANG SECTION GANDA YANG NAMA SECTIONNYA MIRIP JUDUL ANIME ---
            if re.search(r'Episode\s+\d+|Subtitle\s+Indonesia', section_title, re.IGNORECASE):
                continue
            
            items = parse_anime_items(block)
            if items:
                sections.append({
                    "section_name": section_title,
                    "total_items": len(items),
                    "data": items
                })
    
    if not sections:
        global_items = parse_anime_items(soup)
        if global_items:
            sections.append({
                "section_name": "Latest Updates & Releases",
                "total_items": len(global_items),
                "data": global_items
            })
            
    if not sections:
        return {
            "creator": "Vexalyn Developer",
            "statusCode": 404,
            "status": "error",
            "message": "Duh, Zonk bro! Gak ada section konten beranda yang berhasil diparsing.",
            "elapsed_time": f"{elapsed} seconds",
            "sections": []
        }

    return {
        "creator": "Vexalyn Developer",
        "statusCode": 200,
        "status": "success",
        "message": f"Mantap! Berhasil narik konten beranda dengan {len(sections)} section utama.",
        "elapsed_time": f"{elapsed} seconds",
        "sections": sections
    }

async def main():
    print_banner()
    
    await loading_animation("Membangun koneksi ke Anichin", 0.5)
    await loading_animation("Lagi nyari data konten beranda utama", 0.5)
    
    print(f"\n{C_PINK}[*]{RESET} {C_BLUE}Processing payload hook onto target DOM structure...{RESET}")
    
    start_time = time.time()
    result = await scrape_homepage()
    execution_time = round(time.time() - start_time, 2)
    
    print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
    if result["statusCode"] == 200:
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}{result['statusCode']}{RESET}")
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Total Sections:{RESET} {C_CYAN}{len(result['sections'])} sections{RESET}")
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