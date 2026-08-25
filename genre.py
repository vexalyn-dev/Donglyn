# genre.py
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
 [Module]                -> All Genres Scraper Core (genre.py)
 [Target Endpoint]       -> https://anichin.moe/genres/
 [Developer]             -> Vexalyn Developer
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
""")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://anichin.moe/"
}

def scrape_all_genres():
    target_url = "https://anichin.moe/genres/"
    print(f"[*] Menghubungkan ke arsip direktori genre: {target_url}")
    t_start = time.time()
    
    try:
        response = requests.get(target_url, headers=HEADERS, timeout=10)
        elapsed = round(time.time() - t_start, 2)
        
        if response.status_code != 200:
            return {
                "creator": "Vexalyn Developer",
                "statusCode": response.status_code,
                "status": "error",
                "message": f"Gagal mengakses arsip genre. Status code: {response.status_code}"
            }
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Selector kotak genre di halaman anichin.moe/genres/
        genre_elements = soup.select('.genres li a, .taxindex li a, .genre-list li a, .filter.genre li a, a[href*="/genres/"], .tagcloud a, ul.genre li a')
        
        genres_list = []
        seen_slugs = set()
        
        for el in genre_elements:
            raw_text = el.text.strip()
            url = el.get('href')
            
            if raw_text and url and "/genres/" in url:
                if not url.startswith("http"):
                    url = f"https://anichin.moe{url}" if url.startswith('/') else f"https://anichin.moe/{url}"
                
                slug = url.rstrip('/').split('/')[-1]
                
                # Bersihkan angka jumlah donghua di belakang nama genre pakai Regex (misal: "Action 394" jadi "Action")
                clean_name = re.sub(r'\s+\d+$', '', raw_text).strip()
                
                # Filter agar tidak duplikat berdasarkan slug
                if slug and slug not in seen_slugs:
                    seen_slugs.add(slug)
                    genres_list.append({
                        "name": clean_name,
                        "slug": slug,
                        "url": url
                    })
                    
        return {
            "creator": "Vexalyn Developer",
            "statusCode": 200,
            "status": "success",
            "message": f"Berhasil menarik {len(genres_list)} daftar genre bersih dari Anichin",
            "elapsed_time": f"{elapsed} seconds",
            "total_genres": len(genres_list),
            "data": genres_list
        }
        
    except Exception as e:
        return {
            "creator": "Vexalyn Developer",
            "statusCode": 500,
            "status": "error",
            "message": f"Terjadi kesalahan sistem: {str(e)}"
        }

if __name__ == "__main__":
    print("[+] Menjalankan proses ekstraksi seluruh daftar genre secara bersih...")
    result = scrape_all_genres()
    
    print("\n" + "─" * 70)
    print(json.dumps(result, indent=4, ensure_ascii=False))
    print("─" * 70)
    print("[!] Operational complete. Vexalyn Scraper core closed safely.\n")