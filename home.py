# home.py
import sys
import json
import time
import re
import requests
from bs4 import BeautifulSoup

print("""
8888888b.   .d88888b.  888b    888  .d8888b.  888    888 888     888       d8888        .d8888b.   .d8888b.  8888888b.         d8888 8888888b.  8888888888 8888888b. 
888  "Y88b d88P" "Y88b 8888b   888 d88P  Y88b 888    888 888     888      d88888       d88P  Y88b d88P  Y88b 888   Y88b       d88888 888   Y88b 888        888   Y88b
888   888 888   888 88888b  888 888    888 888    888 888     888     d88P888       Y88b.      888   888 888   Y88b      d88P888 888   Y88b 888        888   Y88b
888   888 888   888 888Y88b 888 888        8888888888 888     888    d88P 888        "Y888b.   888        888   d88P     d88P 888 888   d88P 88888e     888   d88P
888   888 888   888 888 Y88b888 888  88888 888    888 888     888   d88P  888           "Y88b. 888        8888888P"     d88P  888 8888888P"  888        8888888P" 
888   888 888   888 888  Y88888 888    888 888    888 888     888  d88P   888             "888 888    888 888 T88b     d88P   888 888        888        888 T88b  
888  .d88P Y88b. .d88P 888   Y8888 Y88b  d88P 888    888 Yb. .d88P d8888888888       Y88b  d88P Y88b  d88P 888   T88b  d8888888888 888        888        888   T88b 
8888888P"   "Y88888P"  888    Y888  "Y8888P88 888    888  "Y88888P" d88P     888        "Y8888P"   "Y8888P"  888    T88b d88P     888 888        8888888888 888    T88b 
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 [Module]                -> Home Page Sections Scraper Core (home.py)
 [Target Endpoint]       -> https://anichin.moe/
 [Developer]             -> Vexalyn Developer
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
""")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://anichin.moe/"
}

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

            thumbnail = img_tag.get('src') or img_tag.get('data-src') if img_tag else ""
            
            # --- EKSTRAKSI EPISODE YANG KETAT & AMAN DARI STATUS ---
            # Prioritaskan elemen badge spesifik di poster
            ep_elem = item.select_one('.epx, .bt .ep, .score')
            episode = ""
            if ep_elem:
                episode = ep_elem.text.strip()
            else:
                # Cek elemen lain, tapi pastikan bukan teks status (Ongoing/Completed)
                for el in item.select('span, div'):
                    txt = el.text.strip()
                    if txt.lower() not in ["ongoing", "completed", "tamat", "hiatus", "sub", "dub"]:
                        if txt.lower().startswith('ep') or re.match(r'^(Ep\s*)?\d+', txt, re.IGNORECASE):
                            episode = txt
                            break
            
            # Jika tetap kosong atau isinya nyasar ke teks status, ambil dari URL
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

def scrape_homepage():
    target_url = "https://anichin.moe/"
    print(f"[*] Menghubungkan ke Beranda Utama: {target_url}")
    t_start = time.time()
    
    try:
        response = requests.get(target_url, headers=HEADERS, timeout=10)
        elapsed = round(time.time() - t_start, 2)
        
        if response.status_code != 200:
            return {
                "creator": "Vexalyn Developer",
                "statusCode": response.status_code,
                "status": "error",
                "message": f"Gagal mengakses beranda Anichin. Status code: {response.status_code}"
            }
            
        soup = BeautifulSoup(response.text, 'html.parser')
        sections = []
        
        block_elements = soup.select('.releases, .section, .widget, .bixbox, div[class*="venz"], div[class*="listupd"]')
        
        for block in block_elements:
            header_tag = block.select_one('h2, h3, h4, .hport span, .releases h2, .widget-title')
            if header_tag:
                section_title = header_tag.text.strip()
                
                # --- FILTER UNTUK MEMBUANG SECTION GANDA YANG NAMA SECTIONNYA MIRIP JUDUL ANIME ---
                # Biasanya section widget satuan memiliki judul yang sangat panjang mengandung kata "Episode" atau "Subtitle Indonesia"
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
            sections.append({
                "section_name": "Latest Updates & Releases",
                "total_items": len(global_items),
                "data": global_items
            })
            
        return {
            "creator": "Vexalyn Developer",
            "statusCode": 200,
            "status": "success",
            "message": f"Berhasil menarik konten beranda dengan {len(sections)} section utama",
            "elapsed_time": f"{elapsed} seconds",
            "sections": sections
        }
        
    except Exception as e:
        return {
            "creator": "Vexalyn Developer",
            "statusCode": 500,
            "status": "error",
            "message": f"Terjadi kesalahan sistem: {str(e)}"
        }

if __name__ == "__main__":
    print("[+] Menjalankan proses ekstraksi konten halaman utama (Home Page)...")
    result = scrape_homepage()
    
    print("\n" + "─" * 70)
    print(json.dumps(result, indent=4, ensure_ascii=False))
    print("─" * 70)
    print("[!] Operational complete. Vexalyn Scraper core closed safely.\n")