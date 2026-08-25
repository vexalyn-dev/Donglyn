# genre_filter.py
import sys
import json
import time
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
 [Module]                -> Genre Filtering Scraper Core (genre_filter.py)
 [Target Endpoint]       -> https://anichin.moe/genres/
 [Developer]             -> Vexalyn Developer
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
""")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://anichin.moe/"
}

def scrape_by_genre(genre_slug: str):
    clean_genre = genre_slug.strip().lower().replace(" ", "-")
    target_url = f"https://anichin.moe/genres/{clean_genre}/"
    
    print(f"[*] Menghubungkan ke arsip genre: {target_url}")
    t_start = time.time()
    
    try:
        response = requests.get(target_url, headers=HEADERS, timeout=10)
        elapsed = round(time.time() - t_start, 2)
        
        if response.status_code != 200:
            return {
                "creator": "Vexalyn Developer",
                "statusCode": response.status_code,
                "status": "error",
                "message": f"Gagal mengakses genre '{clean_genre}'. Status code: {response.status_code}"
            }
            
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('div.utao, article.bs, div.bsx, .kanan, .film-list li')
        
        anime_list = []
        for item in items:
            a_tag = item.select_one('a')
            img_tag = item.select_one('img')
            title_tag = item.select_one('h2, .title, .tt')
            
            if a_tag and a_tag.get('href'):
                url = a_tag.get('href')
                if not url.startswith("http"):
                    url = f"https://anichin.moe{url}" if url.startswith('/') else f"https://anichin.moe/{url}"
                
                raw_title = title_tag.text.strip() if title_tag else (a_tag.get('title') or "Tanpa Judul")
                
                length = len(raw_title)
                half = length // 2
                if length % 2 == 0 and raw_title[:half] == raw_title[half:]:
                    title = raw_title[:half]
                else:
                    title = raw_title

                thumbnail = img_tag.get('src') or img_tag.get('data-src') if img_tag else ""
                
                # Ekstraksi Status (Ongoing / Completed / Hiatus)
                status_badge = item.select_one('.status, .epx, .sb, .ongoing, .completed')
                status_text = status_badge.text.strip() if status_badge else ""
                
                card_text = item.text.lower()
                if not status_text:
                    if "completed" in card_text: status_text = "Completed"
                    elif "ongoing" in card_text: status_text = "Ongoing"
                    elif "hiatus" in card_text: status_text = "Hiatus"
                    else: status_text = "Unknown"

                # Ekstraksi Type (Donghua/Anime) dan Label (Sub/Dub) secara terpisah
                type_val = "Donghua"
                label_val = "Sub"
                
                type_elem = item.select_one('.type, span.type, .bt')
                if type_elem and "anime" in type_elem.text.lower():
                    type_val = "Anime"
                
                label_elem = item.select_one('.sub, span.sub, .term')
                if label_elem:
                    lbl_text = label_elem.text.strip()
                    if lbl_text:
                        label_val = lbl_text

                anime_item = {
                    "title": title,
                    "url": url,
                    "thumbnail": thumbnail,
                    "type": type_val,
                    "label": label_val,
                    "status": status_text
                }
                
                if anime_item not in anime_list:
                    anime_list.append(anime_item)
                    
        return {
            "creator": "Vexalyn Developer",
            "statusCode": 200,
            "status": "success",
            "message": f"Berhasil menarik {len(anime_list)} data dari genre '{clean_genre}'",
            "elapsed_time": f"{elapsed} seconds",
            "total_data": len(anime_list),
            "data": anime_list
        }
        
    except Exception as e:
        return {
            "creator": "Vexalyn Developer",
            "statusCode": 500,
            "status": "error",
            "message": f"Terjadi kesalahan sistem: {str(e)}"
        }

if __name__ == "__main__":
    print("[?] Contoh Genre Populer: action, fantasy, adventure, romance, martial-arts, cultivation")
    genre_input = input("[?] Masukkan Slug/Nama Genre: ").strip()
    
    if not genre_input:
        print("[!] Genre tidak boleh kosong!")
        sys.exit(1)
        
    print("\n[+] Menjalankan proses scraping genre filtering...")
    result = scrape_by_genre(genre_input)
    
    print("\n" + "─" * 70)
    print(json.dumps(result, indent=4, ensure_ascii=False))
    print("─" * 70)
    print("[!] Operational complete. Vexalyn Scraper core closed safely.\n")