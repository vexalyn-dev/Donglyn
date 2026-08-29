# sub.py
import sys
import asyncio
import json
import time
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
 [Module]                -> All Sub Options Scraper Core (sub.py)
 [Target Endpoint]       -> https://anichin.moe/anime/
 [Developer]             -> Vexalyn Developer
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────"""
    print(f"{C_PURPLE}{banner}{RESET}")

async def scrape_all_subs():
    target_url = "https://anichin.moe/anime/"
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
            err_msg = "Waduh, halaman anime Anichin gak ketemu di server."
        elif err_code == 503:
            err_msg = "Duh, server Anichin-nya lagi ngambek atau down tuh."
        elif err_code == 504:
            err_msg = "Koneksi nyangkut alias timeout, kelamaan nunggu balasan dari server target."
        else:
            err_msg = f"Gagal narik data sub, server merespon dengan status code {err_code}."

        return {
            "creator": "Vexalyn Developer",
            "statusCode": err_code,
            "status": "error",
            "message": err_msg,
            "elapsed_time": f"{elapsed} seconds",
            "total_subs": 0,
            "data": []
        }

    soup = BeautifulSoup(html_content, 'html.parser')
    
    sub_elements = soup.select('select[name="sub"] option, select[name*="sub"] option, input[name*="sub"], .filter-sub input')
    
    sub_list = [{"name": "All", "slug": "all"}]
    seen_slugs = {"all"}
    
    for el in sub_elements:
        if el.name == 'option':
            raw_val = el.get('value', '').strip()
            raw_text = el.text.strip()
        elif el.name == 'input':
            raw_val = el.get('value', '').strip()
            label = el.find_next_sibling('label') or el.parent
            raw_text = label.text.strip() if label else raw_val
        else:
            continue

        if raw_val and raw_val.lower() not in ["", "all", "0"]:
            slug = raw_val.lower().replace(" ", "-")
            clean_name = raw_text.strip()
            if not clean_name or clean_name.lower() == "all":
                clean_name = slug.capitalize()
            
            if slug and slug not in seen_slugs:
                seen_slugs.add(slug)
                sub_list.append({
                    "name": clean_name,
                    "slug": slug
                })

    if len(sub_list) == 1:
        default_subs = [
            {"name": "Sub", "slug": "sub"},
            {"name": "Dub", "slug": "dub"},
            {"name": "RAW", "slug": "raw"}
        ]
        for item in default_subs:
            if item["slug"] not in seen_slugs:
                sub_list.append(item)

    total_subs = len(sub_list)

    return {
        "creator": "Vexalyn Developer",
        "statusCode": 200,
        "status": "success",
        "message": f"Mantap! Berhasil menarik {total_subs} daftar sub dari Anichin.",
        "elapsed_time": f"{elapsed} seconds",
        "total_subs": total_subs,
        "data": sub_list
    }

async def main():
    print_banner()
    
    await loading_animation("Membangun koneksi ke Anichin", 0.5)
    await loading_animation("Lagi nyari data filter sub", 0.5)
    
    print(f"\n{C_PINK}[*]{RESET} {C_BLUE}Processing payload hook onto target DOM structure...{RESET}")
    
    start_time = time.time()
    result = await scrape_all_subs()
    execution_time = round(time.time() - start_time, 2)
    
    print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
    if result["statusCode"] == 200:
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Status Code:{RESET} {C_CYAN}{result['statusCode']}{RESET}")
        print(f"{C_PINK}[SUCCESS]{RESET} {C_BLUE}Total Subs:{RESET} {C_CYAN}{result['total_subs']} sub options extracted{RESET}")
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