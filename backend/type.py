# type.py
import sys
import asyncio
import json
import time
import requests
from bs4 import BeautifulSoup
from core.browser import get_page_content

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://anichin.moe/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}

async def get_page_content_fast(url: str):
    def _fetch():
        try:
            r = requests.get(url, headers=HEADERS, timeout=8)
            if r.status_code == 200:
                txt = r.text
                if "Just a moment" in txt or "cf-challenge" in txt.lower() or "Attention Required" in txt:
                    return None, 403
                return txt, 200
            return None, r.status_code
        except Exception:
            return None, 500
    
    res = await asyncio.to_thread(_fetch)
    if isinstance(res, tuple) and len(res) == 2:
        html, code = res
        if html:
            return html, None, code
        else:
            fallback_html = await get_page_content(url)
            return fallback_html, None, code if code else 200
    
    fallback_html = await get_page_content(url)
    return fallback_html, None, 200

C_PURPLE = "\033[35m"
C_PINK = "\033[95m"
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"
C_RED = "\033[91m"
RESET = "\033[0m"

async def loading_animation(text: str, duration: float = 0.8):
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
    """
    print(f"{C_PURPLE}{banner}{RESET}")
    print("─" * 125)
    print(f" {C_PINK}[Module]{RESET}                -> Anichin Type List Extractor (Include All)")
    print(f" {C_PINK}[Target Endpoint]{RESET}       -> https://anichin.moe/anime/")
    print(f" {C_PINK}[Developer]{RESET}             -> Vexalyn Developer")
    print("─" * 125)

async def scrape_type_list():
    target_url = "https://anichin.moe/anime/"
    html_content, error, fetch_code = await get_page_content_fast(target_url)
    
    # Selalu sertakan opsi 'All' di awal
    type_list = [{"name": "All", "value": "all"}]
    
    response = {
        "creator": "Vexalyn Developer",
        "statusCode": fetch_code if fetch_code else 200,
        "status": "success",
        "message": "Mantap! Berhasil mengambil daftar Type Anichin.",
        "ok": True,
        "data": {
            "total_type": 0,
            "type_options": []
        }
    }
    
    if error or fetch_code != 200 or not html_content or not isinstance(html_content, str):
        response["statusCode"] = fetch_code if fetch_code and fetch_code != 200 else 404
        response["status"] = "error"
        response["message"] = f"Duh, zonk bro! Halaman tidak ditemukan (Status Code: {response['statusCode']})."
        response["ok"] = False
        return response

    soup = BeautifulSoup(html_content, 'html.parser')
    
    try:
        options = soup.select('select[name="type"] option, select[name*="type"] option')
        
        for opt in options:
            val = opt.get('value', '').strip()
            name = opt.text.strip()
            if val and val.lower() != "all" and name.lower() != "all":
                type_list.append({"name": name, "value": val})

        if len(type_list) == 1:  # Jika tidak ketangkap lewat select, pakai default lengkap dengan All
            type_list.extend([
                {"name": "Donghua", "value": "donghua"},
                {"name": "Movie", "value": "movie"}
            ])

        response["data"]["total_type"] = len(type_list)
        response["data"]["type_options"] = type_list

    except Exception as e:
        response["statusCode"] = 500
        response["status"] = "error"
        response["message"] = f"Waduh ada error saat parsing type: {str(e)}"
        response["ok"] = False

    return response

async def main():
    print_banner()
    await loading_animation("Menghubungkan ke Anichin Type Engine", 0.4)
    await loading_animation("Mengekstrak daftar type", 0.6)
    
    start_time = time.time()
    result = await scrape_type_list()
    execution_time = round(time.time() - start_time, 2)
    
    print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
    print(C_PINK + "[SUCCESS]" + RESET + " " + C_BLUE + "Status Code:" + RESET + " " + C_CYAN + str(result['statusCode']) + RESET)
    print(C_PINK + "[SUCCESS]" + RESET + " " + C_BLUE + "Total Type:" + RESET + " " + C_CYAN + str(result['data']['total_type']) + " items" + RESET)
    print(C_PINK + "[SUCCESS]" + RESET + " " + C_BLUE + "Elapsed Time:" + RESET + " " + C_CYAN + str(execution_time) + " seconds" + RESET)
    print(f" {C_PURPLE}──────────────────────────────────────────────────────────────────────{RESET}")
    print(f"{C_PINK}[RAW JSON DATA BUFFER]:{RESET}")
    print(f"{C_CYAN}{json.dumps(result, indent=4, ensure_ascii=False)}{RESET}\n")

if __name__ == "__main__":
    asyncio.run(main())