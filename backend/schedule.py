# schedule.py
import re
import time
import sys
import asyncio
import requests
from bs4 import BeautifulSoup
import json

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

def print_ascii_banner():
    banner = r"""
 █████╗ ███╗   ██╗██╗ ██████╗██╗  ██╗██╗███╗   ██╗
██╔══██╗████╗  ██║██║██╔════╝██║  ██║██║████╗  ██║
███████║██╔██╗ ██║██║██║     ███████║██║██╔██╗ ██║
██╔══██║██║╚██╗██║██║██║     ██╔══██║██║██║╚██╗██║
██║  ██║██║ ╚████║██║╚██████╗██║  ██║██║██║ ╚████║
╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
                                                  
    """
    print(f"{C_PURPLE}{banner}{RESET}")
    print("─" * 165)
    print(" [Module]          -> Schedule Scraper (Precise Release Schedule Parser)")
    print(" [Target Endpoint] -> https://anichin.moe/schedule/")
    print(" [Developer]       -> Vexalyn Developer")
    print("─" * 165)

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
            
            status_val = "Ongoing"
            if "completed" in card_text or "tamat" in card_text or "end" in card_text:
                status_val = "Completed"
            elif "hiatus" in card_text:
                status_val = "Hiatus"

            type_val = "Donghua"
            if "anime" in card_text and "donghua" not in card_text:
                type_val = "Anime"

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

async def main():
    print_ascii_banner()
    
    print(f"{C_PINK}[?]{RESET} {C_BLUE}Masukkan Hari (contoh: senin, selasa, rabu, dll. Atau tekan ENTER untuk ambil semua):{RESET}")
    day_input = input(f" {C_PURPLE}╰─>{RESET} ").strip().lower()

    target_url = "https://anichin.moe/schedule/"
    print(f"\n{C_BLUE}[✓] Mengakses target endpoint: {target_url}{RESET}")
    
    t_start = time.time()
    try:
        response = await asyncio.to_thread(requests.get, target_url, headers=HEADERS, timeout=15)
        elapsed = round(time.time() - t_start, 2)
        
        status_code = response.status_code
        html_content = response.text if status_code == 200 else None
        
        if html_content and ("Just a moment" in html_content or "cf-challenge" in html_content.lower()):
            status_code = 403
            html_content = None

        if not html_content or status_code != 200:
            if status_code == 403:
                err_msg = "Yah, diblokir Cloudflare target nih. Coba lagi nanti atau ganti jaringan."
            elif status_code == 404:
                err_msg = "Waduh, halaman jadwal rilis gak ketemu di server."
            elif status_code == 503:
                err_msg = "Duh, server Anichin-nya lagi ngambek atau down tuh."
            elif status_code == 504:
                err_msg = "Koneksi nyangkut alias timeout, kelamaan nunggu balasan dari server target."
            else:
                err_msg = f"Gagal narik halaman jadwal, server merespon dengan status code {status_code}."

            payload = {
                "creator": "Vexalyn Developer",
                "statusCode": status_code,
                "status": "error",
                "message": err_msg,
                "elapsed_time": f"{elapsed} seconds",
                "schedule": []
            }
            
            print(f"\n{C_RED}[ERROR RESPONSE]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}{status_code}{RESET}")
            print(f"{C_RED}[REASON]{RESET} {C_CYAN}{err_msg}{RESET}")
            print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
            print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
            print(f"{C_RED}{json.dumps(payload, indent=4, ensure_ascii=False)}{RESET}")
            print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
            print(f"{C_PINK}[!] Operational complete. Vexalyn Scraper core closed safely.{RESET}\n")
            return

        soup = BeautifulSoup(html_content, 'html.parser')
        
        schedule_data = []
        day_blocks = soup.select('.bixbox, .kg-schedule, div[class*="schedule"], .tab-container, .excstl')
        
        for block in day_blocks:
            day_title_elem = block.select_one('h2, h3, .releases h2, .widget-title, span')
            day_name = day_title_elem.text.strip() if day_title_elem else "Jadwal Rilis"
            
            if day_input and day_input not in day_name.lower():
                continue

            items = parse_anime_items(block)
            if items:
                schedule_data.append({
                    "day": day_name,
                    "total_items": len(items),
                    "data": items
                })

        if len(schedule_data) == 0:
            err_msg = f"Duh, Zonk bro! Gak ada data jadwal rilis untuk hari '{day_input}'." if day_input else "Duh, Zonk bro! Gak ada data jadwal rilis yang berhasil diparsing dari DOM."
            payload = {
                "creator": "Vexalyn Developer",
                "statusCode": 404,
                "status": "error",
                "message": err_msg,
                "elapsed_time": f"{elapsed} seconds",
                "schedule": []
            }
            print(f"\n{C_RED}[ERROR RESPONSE]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}404{RESET}")
            print(f"{C_RED}[REASON]{RESET} {C_CYAN}{err_msg}{RESET}")
            print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
            print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
            print(f"{C_RED}{json.dumps(payload, indent=4, ensure_ascii=False)}{RESET}")
            print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
            print(f"{C_PINK}[!] Operational complete. Vexalyn Scraper core closed safely.{RESET}\n")
            return

        success_msg = f"Mantap! Berhasil nyomot data jadwal rilis untuk hari '{day_input}'." if day_input else "Mantap! Berhasil nyomot data jadwal rilis semua hari."
        payload = {
            "creator": "Vexalyn Developer",
            "statusCode": 200,
            "status": "success",
            "message": success_msg,
            "elapsed_time": f"{elapsed} seconds",
            "schedule": schedule_data
        }

        print(f"\n{C_PINK}[*]{RESET} {C_BLUE}Processing payload hook onto target DOM structure...{RESET}")
        print("─" * 70)
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}200{RESET}")
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Elapsed Time:{RESET} {C_CYAN}{elapsed} seconds{RESET}")
        print("─" * 70)
        print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
        print(f"{C_CYAN}{json.dumps(payload, indent=4, ensure_ascii=False)}{RESET}")
        print("─" * 70)
        print(f"{C_PINK}[!] Operational complete. Vexalyn Scraper core closed safely.{RESET}\n")

    except requests.exceptions.Timeout:
        elapsed = round(time.time() - t_start, 2)
        payload = {
            "creator": "Vexalyn Developer",
            "statusCode": 504,
            "status": "error",
            "message": "Koneksi nyangkut alias timeout, kelamaan nunggu balasan dari server target.",
            "elapsed_time": f"{elapsed} seconds",
            "schedule": []
        }
        print(f"\n{C_RED}[ERROR RESPONSE]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}504{RESET}")
        print(f"{C_RED}[REASON]{RESET} {C_CYAN}Koneksi nyangkut alias timeout, kelamaan nunggu balasan dari server target.{RESET}")
        print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
        print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
        print(f"{C_RED}{json.dumps(payload, indent=4, ensure_ascii=False)}{RESET}")
        print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
        print(f"{C_PINK}[!] Operational complete. Vexalyn Scraper core closed safely.{RESET}\n")
    except requests.exceptions.ConnectionError:
        elapsed = round(time.time() - t_start, 2)
        payload = {
            "creator": "Vexalyn Developer",
            "statusCode": 503,
            "status": "error",
            "message": "Duh, server Anichin-nya lagi ngambek atau down tuh (Connection Error).",
            "elapsed_time": f"{elapsed} seconds",
            "schedule": []
        }
        print(f"\n{C_RED}[ERROR RESPONSE]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}503{RESET}")
        print(f"{C_RED}[REASON]{RESET} {C_CYAN}Duh, server Anichin-nya lagi ngambek atau down tuh (Connection Error).{RESET}")
        print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
        print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
        print(f"{C_RED}{json.dumps(payload, indent=4, ensure_ascii=False)}{RESET}")
        print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
        print(f"{C_PINK}[!] Operational complete. Vexalyn Scraper core closed safely.{RESET}\n")
    except Exception as e:
        elapsed = round(time.time() - t_start, 2)
        payload = {
            "creator": "Vexalyn Developer",
            "statusCode": 500,
            "status": "error",
            "message": f"Terjadi kesalahan internal: {str(e)}",
            "elapsed_time": f"{elapsed} seconds",
            "schedule": []
        }
        print(f"\n{C_RED}[ERROR RESPONSE]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}500{RESET}")
        print(f"{C_RED}[REASON]{RESET} {C_CYAN}Terjadi kesalahan internal: {str(e)}{RESET}")
        print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
        print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
        print(f"{C_RED}{json.dumps(payload, indent=4, ensure_ascii=False)}{RESET}")
        print(f"{C_PURPLE} ──────────────────────────────────────────────────────────────────────{RESET}")
        print(f"{C_PINK}[!] Operational complete. Vexalyn Scraper core closed safely.{RESET}\n")

if __name__ == '__main__':
    asyncio.run(main())