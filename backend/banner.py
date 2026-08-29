# banner.py
import re
import time
import requests
from bs4 import BeautifulSoup
import json

# ANSI Colors - Tema Pink, Ungu, Biru
C_PURPLE = "\033[35m"
C_PINK = "\033[95m"
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"
C_RED = "\033[91m"
RESET = "\033[0m"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://anichin.moe/"
}

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
    print("─" * 105)
    print(f" {C_PINK}[Module]{RESET}          -> Banner Slider Scraper (Backdrop Div Parser)")
    print(f" {C_PINK}[Target Endpoint]{RESET} -> https://anichin.moe (Homepage Banner)")
    print(f" {C_PINK}[Developer]{RESET}       -> Vexalyn Developer")
    print("─" * 105)

def scrape_banner():
    print_ascii_banner()
    target_url = "https://anichin.moe/"
    print(f"{C_PINK}[✓]{RESET} {C_BLUE}Mengakses target endpoint: {C_CYAN}{target_url}{RESET}")
    
    t_start = time.time()
    try:
        response = requests.get(target_url, headers=HEADERS, timeout=15)
        elapsed = round(time.time() - t_start, 2)
        
        if response.status_code != 200:
            err_payload = {
                "creator": "Vexalyn Developer",
                "statusCode": response.status_code,
                "status": "error",
                "message": f"Gagal mengakses halaman target. Status Code: {response.status_code}",
                "elapsed_time": f"{elapsed} seconds"
            }
            print(f"\n{C_RED}[!] Gagal mengakses halaman. Status Code: {response.status_code}{RESET}")
            print(json.dumps(err_payload, indent=4, ensure_ascii=False))
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        banner_list = []
        slider_container = soup.select_one('#slidertwo')
        
        if slider_container:
            # Mengambil tiap elemen slide di dalam swiper container
            slides = slider_container.select('.swiper-slide')
            for slide in slides:
                # Hindari duplicate slide dari swiper loop mode
                if 'swiper-slide-duplicate' in slide.get('class', []):
                    continue

                a_tag = slide.select_one('a')
                title_tag = slide.select_one('.title, h2, h3, .tt')
                desc_tag = slide.select_one('.desc, p, .entry-content')
                backdrop_div = slide.select_one('.backdrop')
                
                if a_tag and a_tag.get('href'):
                    url = a_tag.get('href')
                    if not url.startswith("http"):
                        url = f"https://anichin.moe{url}" if url.startswith('/') else f"https://anichin.moe/{url}"
                    
                    title = title_tag.text.strip() if title_tag else (a_tag.get('title') or "Featured Banner")
                    
                    # --- EKSTRAKSI THUMBNAIL DARI DIV BACKDROP ---
                    thumbnail = ""
                    if backdrop_div:
                        style_attr = backdrop_div.get('style', '')
                        if 'background-image' in style_attr:
                            match_bg = re.search(r"url\((['\"]?)(.*?)\1\)", style_attr)
                            if match_bg:
                                thumbnail = match_bg.group(2)
                    
                    # Fallback jika .backdrop tidak ketangkap, cek style langsung di slide
                    if not thumbnail:
                        style_attr = slide.get('style', '')
                        if 'background-image' in style_attr:
                            match_bg = re.search(r"url\((['\"]?)(.*?)\1\)", style_attr)
                            if match_bg:
                                thumbnail = match_bg.group(2)

                    synopsis = desc_tag.text.strip() if desc_tag else ""
                    
                    banner_item = {
                        "title": title,
                        "url": url,
                        "thumbnail": thumbnail,
                        "synopsis": synopsis
                    }
                    
                    if banner_item not in banner_list:
                        banner_list.append(banner_item)

        payload = {
            "creator": "Vexalyn Developer",
            "statusCode": 200,
            "status": "success",
            "elapsed_time": f"{elapsed} seconds",
            "total_banners": len(banner_list),
            "banners": banner_list
        }

        print(f"\n{C_PINK}[*]{RESET} {C_BLUE}Processing payload hook onto target DOM structure...{RESET}")
        print("─" * 70)
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Status Code: {C_CYAN}{response.status_code}{RESET}")
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Elapsed Time: {C_CYAN}{elapsed} seconds{RESET}")
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Total Banners Found: {C_CYAN}{len(banner_list)}{RESET}")
        print("─" * 70)
        print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
        print(f"{C_CYAN}{json.dumps(payload, indent=4, ensure_ascii=False)}{RESET}")
        print("─" * 70)
        print(f"{C_PINK}[!]{RESET} {C_BLUE}Operational complete. Vexalyn Scraper core closed safely.{RESET}")

    except Exception as e:
        err_payload = {
            "creator": "Vexalyn Developer",
            "statusCode": 500,
            "status": "error",
            "message": str(e)
        }
        print(f"{C_RED}[!] Terjadi error saat scraping banner: {str(e)}{RESET}")
        print(json.dumps(err_payload, indent=4, ensure_ascii=False))

if __name__ == '__main__':
    scrape_banner()