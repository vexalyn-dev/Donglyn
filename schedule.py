# schedule.py
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
    print(" [Module]         -> Schedule Scraper (Precise Release Schedule Parser)")
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

            thumbnail = img_tag.get('src') or img_tag.get('data-src') if img_tag else ""
            
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

def scrape_schedule():
    print_ascii_banner()
    target_url = "https://anichin.moe/schedule/"
    print(f"[✓] Mengakses target endpoint: {target_url}")
    
    t_start = time.time()
    try:
        response = requests.get(target_url, headers=HEADERS, timeout=15)
        elapsed = round(time.time() - t_start, 2)
        
        if response.status_code != 200:
            print(f"[!] Gagal mengakses halaman. Status Code: {response.status_code}")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        schedule_data = []
        day_blocks = soup.select('.bixbox, .kg-schedule, div[class*="schedule"], .tab-container, .excstl')
        
        for block in day_blocks:
            day_title_elem = block.select_one('h2, h3, .releases h2, .widget-title, span')
            day_name = day_title_elem.text.strip() if day_title_elem else "Jadwal Rilis"
            items = parse_anime_items(block)
            if items:
                schedule_data.append({
                    "day": day_name,
                    "total_items": len(items),
                    "data": items
                })

        payload = {
            "creator": "Vexalyn Developer",
            "statusCode": 200,
            "status": "success",
            "elapsed_time": f"{elapsed} seconds",
            "schedule": schedule_data
        }

        print("\n[*] Processing payload hook onto target DOM structure...")
        print("─" * 70)
        print(f"[SUCCESS] Status Code: {response.status_code}")
        print(f"[SUCCESS] Elapsed Time: {elapsed} seconds")
        print("─" * 70)
        print("[RAW JSON DATA BUFFER]:")
        print(json.dumps(payload, indent=4, ensure_ascii=False))
        print("─" * 70)
        print("[!] Operational complete. Vexalyn Scraper core closed safely.")

    except Exception as e:
        print(f"[!] Terjadi error saat scraping: {str(e)}")

if __name__ == '__main__':
    scrape_schedule()