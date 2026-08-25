# banner.py
import re
import time
import requests
from bs4 import BeautifulSoup
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://anichin.moe/"
}

def print_ascii_banner():
    banner = """
    8888888b.  .d88888b.  888b    888  .d8888b.  888    888 888     888       d8888        .d8888b.    .d8888b.  8888888b.       d8888 8888888b.  8888888888 8888888b. 
    888  "Y88b d88P" "Y88b 8888b   888 d88P  Y88b 888    888 888     888      d88888       d88P  Y88b d88P  Y88b 888  "Y88b     d88888 888   Y88b 888        888   Y88b
    888    888 888     888 88888b  888 888    888 888    888 888     888     d88P888       Y88b.      888    888 888    888   d88P888 888    888 888        888    888
    888    888 888     888 888Y88b 888 888        8888888888 888     888    d88P 888        "Y888b.   888        888   d88P  d88P 888 888   d88P 88888      888   d88P
    888    888 888     888 888 Y88b888 888  88888 888    888 888     888   d88P  888           "Y88b. 888        8888888P"  d88P  888 8888888P"  888        8888888P" 
    888    888 888     888 888  Y88888 888    888 888    888 888     888  d88P   888             "888 888    888 888 T88b  d88P   888 888        888        888 T88b  
    888  .d88P Y88b. .d88P 888   Y8888 Y88b  d88P 888    888 Y88b. .d88P d8888888888       Y88b  d88P Y88b  d88P 888  T88b d8888888888 888        8888888888 888  T88b 
    8888888P"   "Y88888P"  888    Y888  "Y8888P88 888    888  "Y88888P" d88P     888        "Y8888P"   "Y8888P"  888   T88b d88P     888 888        8888888888 888   T88b
    """
    print(banner)
    print("─" * 165)
    print(" [Module]         -> Banner Slider Scraper (Backdrop Div Parser)")
    print(" [Target Endpoint] -> https://anichin.moe (Homepage Banner)")
    print(" [Developer]       -> Vexalyn Developer")
    print("─" * 165)

def scrape_banner():
    print_ascii_banner()
    target_url = "https://anichin.moe/"
    print(f"[✓] Mengakses target endpoint: {target_url}")
    
    t_start = time.time()
    try:
        response = requests.get(target_url, headers=HEADERS, timeout=15)
        elapsed = round(time.time() - t_start, 2)
        
        if response.status_code != 200:
            print(f"[!] Gagal mengakses halaman. Status Code: {response.status_code}")
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

        print("\n[*] Processing payload hook onto target DOM structure...")
        print("─" * 70)
        print(f"[SUCCESS] Status Code: {response.status_code}")
        print(f"[SUCCESS] Elapsed Time: {elapsed} seconds")
        print(f"[SUCCESS] Total Banners Found: {len(banner_list)}")
        print("─" * 70)
        print("[RAW JSON DATA BUFFER]:")
        print(json.dumps(payload, indent=4, ensure_ascii=False))
        print("─" * 70)
        print("[!] Operational complete. Vexalyn Scraper core closed safely.")

    except Exception as e:
        print(f"[!] Terjadi error saat scraping banner: {str(e)}")

if __name__ == '__main__':
    scrape_banner()