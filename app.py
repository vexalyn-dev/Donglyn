# app.py — Netflix + Auth + Fallback + Proxy Anti-403 + Banner + Schedule
import sys, asyncio, urllib.parse
from flask import Flask, jsonify, request, render_template, redirect, url_for, session, send_from_directory, Response, stream_with_context
import time, re, requests, os, sqlite3, secrets, json, base64
from urllib.parse import quote, unquote, urljoin, urlparse
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

try:
    import google.auth.transport.requests  # type: ignore
    from google.oauth2 import id_token  # type: ignore
    HAS_GOOGLE_AUTH = True
except ImportError:
    HAS_GOOGLE_AUTH = False

try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config['UPLOAD_FOLDER'] = os.path.join('static','uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 30
ALLOWED_EXT = {'png','jpg','jpeg','webp','gif'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
FONNTE_TOKEN = os.environ.get("FONNTE_TOKEN", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://anichin.moe/",
    "Origin": "https://anichin.moe",
}

def resolve_episode_url(query: str):
    clean_query = query.strip()
    if clean_query.startswith("http"):
        return clean_query
    if "episode" in clean_query.lower():
        slug = clean_query.lower().strip('/')
        slug = "".join([c if c.isalnum() or c.isspace() else "" for c in slug])
        slug = "-".join(slug.split())
        return f"https://anichin.moe/{slug}/"
    encoded_query = urllib.parse.quote(clean_query)
    search_url = f"https://anichin.moe/?s={encoded_query}"
    try:
        res = requests.get(search_url, headers=HEADERS, timeout=5)
        if res.status_code != 200:
            return None
        soup = BeautifulSoup(res.text, 'html.parser')
        first_item = soup.select_one('div.utao a, article.bs a, div.bsx a, .kanan h2 a, .film-list li a')
        if not first_item or not first_item.get('href'):
            return None
        matched_url = first_item.get('href')
        if not matched_url.startswith("http"):
            matched_url = f"https://anichin.moe{matched_url}" if matched_url.startswith('/') else f"https://anichin.moe/{matched_url}"
        if "episode" in matched_url.lower():
            return matched_url
        res_main = requests.get(matched_url, headers=HEADERS, timeout=5)
        if res_main.status_code == 200:
            soup_main = BeautifulSoup(res_main.text, 'html.parser')
            ep_latest = soup_main.select_one('div.episodelist ul li:first-child a, ul.daftarep li:first-child a, .eplister ul li:first-child a')
            if ep_latest and ep_latest.get('href'):
                ep_url = ep_latest.get('href')
                return ep_url if ep_url.startswith("http") else f"https://anichin.moe{ep_url}"
        return matched_url
    except Exception:
        return None

async def scrape_iframe_async(target_url, server_keyword):
    if async_playwright is None:
        return None
    iframe_url = None
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu"])
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = await context.new_page()
        try:
            await page.route("**/*.{png,jpg,jpeg,gif,svg,css,ico}", lambda route: route.abort())
            await page.goto(target_url, wait_until="domcontentloaded", timeout=10000)
            await asyncio.sleep(0.5)
            locators = page.locator('.mobius select option, .pushserver option, ul.player-server li, .select-server li, div.player_option, div.pselect select option, .server_option, .eps-item, select#select-server option')
            count = await locators.count()
            target_locator = None
            for i in range(count):
                item = locators.nth(i)
                text = (await item.inner_text()).strip()
                if server_keyword.lower() in text.lower():
                    target_locator = item
                    break
            if target_locator:
                tag_name = await target_locator.evaluate("el => el.tagName.toLowerCase()")
                if tag_name == "option":
                    parent_select = target_locator.locator("xpath=ancestor::select")
                    if await parent_select.count() > 0:
                        val = await target_locator.get_attribute("value")
                        await parent_select.select_option(value=val)
                    else:
                        await target_locator.click(force=True)
                else:
                    await target_locator.click(force=True)
                await asyncio.sleep(0.8)
            else:
                if count > 0:
                    await locators.nth(0).click(force=True)
                    await asyncio.sleep(0.8)
            current_html = await page.content()
            current_soup = BeautifulSoup(current_html, 'html.parser')
            iframe = current_soup.select_one('iframe, .pframe iframe, div.player-embed iframe, div#pframe iframe')
            if iframe:
                src = iframe.get('src') or iframe.get('data-src')
                if src and "googleads" not in src:
                    iframe_url = f"https://anichin.moe{src}" if src.startswith('/') else src
        except Exception:
            pass
        await browser.close()
    return iframe_url

DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

# ---------- DB ----------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT,
        password_hash TEXT,
        avatar TEXT,
        google_id TEXT,
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    # Add phone column if missing (migration)
    try:
        conn.execute("SELECT phone FROM users LIMIT 1")
    except:
        conn.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    conn.commit()
    conn.close()

# OTP storage (in-memory, for production use Redis or DB)
otp_store = {}

init_db()

def get_current_user():
    uid = session.get('user_id')
    if not uid: return None
    conn = get_db()
    row = conn.execute('SELECT * FROM users WHERE id=?', (uid,)).fetchone()
    conn.close()
    return dict(row) if row else None

def login_required(f):
    @wraps(f)
    def wrap(*a, **kw):
        if not session.get('user_id'):
            if request.accept_mimetypes.accept_json or request.path.startswith('/api/'):
                return jsonify({"status":"error","message":"Login required"}), 401
            return redirect(url_for('login_page'))
        return f(*a, **kw)
    return wrap

def allowed_file(fn):
    return '.' in fn and fn.rsplit('.',1)[1].lower() in ALLOWED_EXT

# ---------- Mock fallback ----------
MOCK_SECTIONS = [
    {
        "section_name": "Trending Now — Donghua Hot",
        "total_items": 6,
        "data": [
            {"title":"Battle Through the Heavens","url":"/detail?url=https://anichin.moe/btth/","original_url":"https://anichin.moe/btth/","thumbnail":"https://cdn.myanimelist.net/images/anime/1208/94745.jpg","episode":"Ep 120","type":"Donghua","label":"SUB","status":"Ongoing"},
            {"title":"Perfect World","url":"/detail?url=https://anichin.moe/perfect-world/","original_url":"https://anichin.moe/perfect-world/","thumbnail":"https://cdn.myanimelist.net/images/anime/10/76045.jpg","episode":"Ep 185","type":"Donghua","label":"SUB","status":"Ongoing"},
            {"title":"Soul Land 2","url":"/detail?url=https://anichin.moe/soul-land-2/","original_url":"https://anichin.moe/soul-land-2/","thumbnail":"https://cdn.myanimelist.net/images/anime/1356/130543.jpg","episode":"Ep 58","type":"Donghua","label":"SUB","status":"Completed"},
            {"title":"Tales of Demons and Gods","url":"/detail?url=https://anichin.moe/tales-of-demons/","original_url":"https://anichin.moe/tales-of-demons/","thumbnail":"https://picsum.photos/300/450?random=11","episode":"Ep 252","type":"Donghua","label":"DUB","status":"Ongoing"},
            {"title":"Apotheosis","url":"/detail?url=https://anichin.moe/apotheosis/","original_url":"https://anichin.moe/apotheosis/","thumbnail":"https://picsum.photos/300/450?random=12","episode":"Ep 112","type":"Donghua","label":"SUB","status":"Ongoing"},
            {"title":"Renegade Immortal","url":"/detail?url=https://anichin.moe/renegade-immortal/","original_url":"https://anichin.moe/renegade-immortal/","thumbnail":"https://picsum.photos/300/450?random=13","episode":"Ep 74","type":"Donghua","label":"SUB","status":"Ongoing"},
        ]
    },
    {
        "section_name": "Baru Rilis — Update Hari Ini",
        "total_items": 6,
        "data": [
            {"title":"Throne of Seal","url":"/detail?url=https://anichin.moe/throne-of-seal/","original_url":"https://anichin.moe/throne-of-seal/","thumbnail":"https://picsum.photos/300/450?random=21","episode":"Ep 92","type":"Donghua","label":"SUB","status":"Ongoing"},
            {"title":"Against the Gods","url":"/detail?url=https://anichin.moe/against-the-gods/","original_url":"https://anichin.moe/against-the-gods/","thumbnail":"https://picsum.photos/300/450?random=22","episode":"Ep 45","type":"Donghua","label":"SUB","status":"Ongoing"},
            {"title":"Stellar Transformations","url":"/detail?url=https://anichin.moe/stellar/","original_url":"https://anichin.moe/stellar/","thumbnail":"https://picsum.photos/300/450?random=23","episode":"Ep 60","type":"Donghua","label":"SUB","status":"Ongoing"},
            {"title":"A Will Eternal","url":"/detail?url=https://anichin.moe/a-will-eternal/","original_url":"https://anichin.moe/a-will-eternal/","thumbnail":"https://picsum.photos/300/450?random=24","episode":"Ep 82","type":"Donghua","label":"DUB","status":"Completed"},
            {"title":"Martial Universe","url":"/detail?url=https://anichin.moe/martial-universe/","original_url":"https://anichin.moe/martial-universe/","thumbnail":"https://picsum.photos/300/450?random=25","episode":"Ep 98","type":"Donghua","label":"SUB","status":"Ongoing"},
            {"title":"Wo Jia Da Shixiong","url":"/detail?url=https://anichin.moe/wo-jia/","original_url":"https://anichin.moe/wo-jia/","thumbnail":"https://picsum.photos/300/450?random=26","episode":"Ep 40","type":"Donghua","label":"SUB","status":"Ongoing"},
        ]
    },
    {
        "section_name": "Top 10 Donghua Minggu Ini",
        "total_items": 6,
        "data": [
            {"title":"One Hundred Thousand Years","url":"/detail?url=https://anichin.moe/100k-years/","original_url":"https://anichin.moe/100k-years/","thumbnail":"https://picsum.photos/300/450?random=31","episode":"Ep 156","type":"Donghua","label":"SUB","status":"Ongoing"},
            {"title":"Dragon Prince Yuan","url":"/detail?url=https://anichin.moe/yuan/","original_url":"https://anichin.moe/yuan/","thumbnail":"https://picsum.photos/300/450?random=32","episode":"Ep 52","type":"Donghua","label":"SUB","status":"Ongoing"},
            {"title":"Jade Dynasty","url":"/detail?url=https://anichin.moe/jade-dynasty/","original_url":"https://anichin.moe/jade-dynasty/","thumbnail":"https://picsum.photos/300/450?random=33","episode":"Ep 64","type":"Donghua","label":"SUB","status":"Completed"},
            {"title":"The Great Ruler","url":"/detail?url=https://anichin.moe/great-ruler/","original_url":"https://anichin.moe/great-ruler/","thumbnail":"https://picsum.photos/300/450?random=34","episode":"Ep 88","type":"Donghua","label":"SUB","status":"Ongoing"},
            {"title":"Tales of Androgyny","url":"/detail?url=https://anichin.moe/androgyny/","original_url":"https://anichin.moe/androgyny/","thumbnail":"https://picsum.photos/300/450?random=35","episode":"Ep 30","type":"Donghua","label":"DUB","status":"Ongoing"},
            {"title":"My Wife Comes From","url":"/detail?url=https://anichin.moe/my-wife/","original_url":"https://anichin.moe/my-wife/","thumbnail":"https://picsum.photos/300/450?random=36","episode":"Ep 14","type":"Donghua","label":"SUB","status":"Ongoing"},
        ]
    }
]

MOCK_BANNERS = [
    {"title":"Battle Through the Heavens","url":"https://anichin.moe/btth/","thumbnail":"https://cdn.myanimelist.net/images/anime/1208/94745.jpg","synopsis":"Xiao Yan berjuang kultivasi dari nol menuju puncak Dou Qi — donghua paling populer minggu ini."},
    {"title":"Perfect World","url":"https://anichin.moe/perfect-world/","thumbnail":"https://cdn.myanimelist.net/images/anime/10/76045.jpg","synopsis":"Shi Hao lahir dengan tulang supreme, hadapi takdir kejam demi jadi emperor abadi."},
    {"title":"Soul Land 2","url":"https://anichin.moe/soul-land-2/","thumbnail":"https://cdn.myanimelist.net/images/anime/1356/130543.jpg","synopsis":"Generasi baru Shrek Academy melawan roh jahat di dunia spirit master."},
    {"title":"Throne of Seal","url":"https://anichin.moe/throne-of-seal/","thumbnail":"https://picsum.photos/1200/600?random=21","synopsis":"Long Haochen tempa throne suci melawan kegelapan."},
    {"title":"Tales of Demons and Gods","url":"https://anichin.moe/tales-of-demons/","thumbnail":"https://picsum.photos/1200/600?random=22","synopsis":"Nie Li reinkarnasi bawa pengetahuan masa depan selamatkan kota."},
    {"title":"Apotheosis","url":"https://anichin.moe/apotheosis/","thumbnail":"https://picsum.photos/1200/600?random=23","synopsis":"Zen Luo tembus batas kultivasi dari budak jadi legenda."},
    {"title":"Renegade Immortal","url":"https://anichin.moe/renegade-immortal/","thumbnail":"https://picsum.photos/1200/600?random=24","synopsis":"Wang Lin taklukkan immortal dengan tekad baja."},
    {"title":"Stellar Transformations","url":"https://anichin.moe/stellar-transformations/","thumbnail":"https://picsum.photos/1200/600?random=25","synopsis":"Qin Yu ubah tubuh bintang capai keabadian."},
    {"title":"A Will Eternal","url":"https://anichin.moe/a-will-eternal/","thumbnail":"https://picsum.photos/1200/600?random=26","synopsis":"Bai Xiaochun kejar hidup abadi dengan cara kocak nan epic."},
    {"title":"Martial Universe","url":"https://anichin.moe/martial-universe/","thumbnail":"https://picsum.photos/1200/600?random=27","synopsis":"Lin Dong bangkit dari hinaan jadi penguasa martial."},
    {"title":"Dragon Prince Yuan","url":"https://anichin.moe/yuan/","thumbnail":"https://picsum.photos/1200/600?random=28","synopsis":"Zhou Yuan rebut kembali naga suci kerajaan."},
    {"title":"The Great Ruler","url":"https://anichin.moe/great-ruler/","thumbnail":"https://picsum.photos/1200/600?random=29","synopsis":"Mu Chen taklukkan Great Thousand World."},
    {"title":"One Hundred Thousand Years","url":"https://anichin.moe/100k-years/","thumbnail":"https://picsum.photos/1200/600?random=30","synopsis":"Master abadi bimbing murid selama 100 ribu tahun."},
    {"title":"Jade Dynasty","url":"https://anichin.moe/jade-dynasty/","thumbnail":"https://picsum.photos/1200/600?random=31","synopsis":"Zhang Xiaofan hadapi cinta dan takdir di sekte Qingyun."},
    {"title":"Against the Gods","url":"https://anichin.moe/against-the-gods/","thumbnail":"https://picsum.photos/1200/600?random=32","synopsis":"Yun Che bangkit dengan darah Phoenix taklukkan dewa."},
]

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
            local_detail_url = f"/detail?url={url}"
            raw_title = title_tag.text.strip() if title_tag else (a_tag.get('title') or "")
            if not raw_title and a_tag.get('title'):
                raw_title = a_tag.get('title')
            clean_title = re.sub(r'\s*Episode\s+\d+.*$', '', raw_title, flags=re.IGNORECASE).strip()
            clean_title = re.sub(r'\s*Subtitle\s+Indonesia.*$', '', clean_title, flags=re.IGNORECASE).strip()
            length = len(clean_title); half = length // 2
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
                    if txt.lower() not in ["ongoing","completed","tamat","hiatus","sub","dub"]:
                        if txt.lower().startswith('ep') or re.match(r'^(Ep\s*)?\d+', txt, re.IGNORECASE):
                            episode = txt; break
            if not episode or episode.lower() in ["ongoing","completed","tamat","hiatus"]:
                url_match = re.search(r'episode-(\d+|[a-z0-9-]+)', url)
                if url_match:
                    ep_slug = url_match.group(1).replace('-',' ')
                    episode = f"Ep {ep_slug}" if ep_slug.isdigit() else ep_slug.title()
                else:
                    episode = "Movie" if "movie" in url else "Unknown"
            card_text = item.text.lower()
            status_val = "Ongoing"
            if "completed" in card_text or "tamat" in card_text or "end" in card_text: status_val="Completed"
            elif "hiatus" in card_text: status_val="Hiatus"
            type_val = "Donghua"
            if "anime" in card_text and "donghua" not in card_text: type_val="Anime"
            label_val="Sub"
            label_elem=item.select_one('.sub, span.sub, .term')
            if label_elem:
                lbl=label_elem.text.strip()
                if lbl: label_val=lbl
            elif "dub" in card_text: label_val="Dub"
            anime_item={"title":title,"url":local_detail_url,"original_url":url,"thumbnail":thumbnail,"episode":episode,"type":type_val,"label":label_val,"status":status_val}
            if anime_item not in anime_list:
                anime_list.append(anime_item)
    return anime_list

def scrape_banner_data():
    target_url = "https://anichin.moe/"
    try:
        r = requests.get(target_url, headers=HEADERS, timeout=12)
        if r.status_code != 200:
            return MOCK_BANNERS
        soup = BeautifulSoup(r.text, 'html.parser')
        banner_list = []
        slider = soup.select_one('#slidertwo')
        if slider:
            slides = slider.select('.swiper-slide')
            for slide in slides:
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
                    thumbnail = ""
                    if backdrop_div:
                        style_attr = backdrop_div.get('style','')
                        if 'background-image' in style_attr:
                            m = re.search(r"url\((['\"]?)(.*?)\1\)", style_attr)
                            if m: thumbnail = m.group(2)
                    if not thumbnail:
                        style_attr = slide.get('style','')
                        if 'background-image' in style_attr:
                            m = re.search(r"url\((['\"]?)(.*?)\1\)", style_attr)
                            if m: thumbnail = m.group(2)
                    synopsis = desc_tag.text.strip() if desc_tag else ""
                    item = {"title":title,"url":url,"thumbnail":thumbnail or "https://picsum.photos/1200/600?random=90","synopsis":synopsis or "Streaming donghua sub Indo kualitas HD."}
                    if item not in banner_list:
                        banner_list.append(item)
        if not banner_list:
            return MOCK_BANNERS
        return banner_list[:15]
    except Exception as e:
        return MOCK_BANNERS

def scrape_schedule_data():
    target_url = "https://anichin.moe/schedule/"
    try:
        r = requests.get(target_url, headers=HEADERS, timeout=12)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, 'html.parser')
        schedule_data=[]
        day_blocks = soup.select('.bixbox, .kg-schedule, div[class*="schedule"], .tab-container, .excstl')
        for block in day_blocks:
            day_title = block.select_one('h2, h3, .releases h2, .widget-title, span')
            day_name = day_title.text.strip() if day_title else "Jadwal Rilis"
            if len(day_name) > 30: continue
            items = parse_anime_items(block)
            if items:
                schedule_data.append({"day":day_name,"total_items":len(items),"data":items})
        if not schedule_data:
            # fallback: bikin dari MOCK
            schedule_data = [{"day":"Senin","total_items":3,"data":MOCK_SECTIONS[0]["data"][:3]}, {"day":"Rabu","total_items":3,"data":MOCK_SECTIONS[1]["data"][:3]}]
        return schedule_data
    except Exception:
        return []

@app.route('/asset/<path:filename>')
@app.route('/assets/<path:filename>')
def serve_asset(filename):
    for folder in ['assets', 'asset', 'static']:
        base = os.path.join(app.root_path, folder)
        if os.path.isdir(base):
            # case-insensitive lookup
            for fname in os.listdir(base):
                if fname.lower() == filename.lower():
                    return send_from_directory(base, fname)
            full = os.path.join(base, filename)
            if os.path.exists(full):
                return send_from_directory(base, filename)
    return send_from_directory(os.path.join(app.root_path, 'assets'), filename)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.svg', mimetype='image/svg+xml')

# ---------- Pages ----------
@app.route('/')
def index():
    user = get_current_user()
    return render_template('index.html', user=user)

@app.route('/detail')
def detail_page():
    target_url = request.args.get('url')
    if not target_url:
        return "URL tidak ditemukan", 400
    user = get_current_user()
    return render_template('detail.html', target_url=target_url, user=user)

@app.route('/login')
def login_page():
    if session.get('user_id'): return redirect(url_for('index'))
    return render_template('login.html', client_id=GOOGLE_CLIENT_ID)

@app.route('/register')
def register_page():
    if session.get('user_id'): return redirect(url_for('index'))
    return render_template('register.html', client_id=GOOGLE_CLIENT_ID)

@app.route('/forgot-password')
def forgot_password_page():
    return render_template('forgot.html')

@app.route('/genre')
def genre_page():
    user = get_current_user()
    return render_template('genre.html', user=user)

@app.route('/schedule')
def schedule_page():
    user = get_current_user()
    return render_template('schedule.html', user=user)

@app.route('/bookmark')
def bookmark_page():
    user = get_current_user()
    return render_template('bookmark.html', user=user)

@app.route('/riwayat')
def riwayat_page():
    user = get_current_user()
    return render_template('riwayat.html', user=user)

@app.route('/section')
def section_page():
    url = request.args.get('url')
    name = request.args.get('name', 'Section')
    user = get_current_user()
    return render_template('section.html', url=url, name=name, user=user)

@app.route('/profile')
@login_required
def profile_page():
    user = get_current_user()
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout_page():
    session.clear()
    return redirect(url_for('index'))

@app.route('/player')
@app.route('/watch')
def player_page():
    url = request.args.get('url') or request.args.get('episode') or ""
    server = request.args.get('server') or ""
    if not url:
        url = request.args.get('u') or ""
    if not url:
        return redirect(url_for('index'))
    if not url.startswith("http"):
        url = "https://anichin.moe/" + url.lstrip("/")
    title = "Player Vexora"
    iframe_url = ""
    servers = []
    clean_url = re.sub(r'https?://anichin\.moe/', '', url).strip('/').replace('/','-')[:60] or "episode"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(resp.text, 'html.parser')
        t = soup.select_one('h1.entry-title, h1')
        if t: title = t.text.strip()
        for el in soup.select('select option, .player-server li, ul.server-list li, .server_option, .pserver'):
            txt = el.text.strip()
            if txt and len(txt)<30 and txt.lower() not in ["pilih server","select server"]:
                servers.append(txt)
        seen=set(); uniq=[]
        for s in servers:
            if s not in seen:
                seen.add(s); uniq.append(s)
        servers = uniq[:12]
        if not servers:
            for a in soup.select('.misha_load, [data-server]'):
                txt = a.get_text(strip=True) or a.get('data-server')
                if txt: servers.append(txt)
            servers = list(dict.fromkeys(servers))[:12]
        iframe = soup.select_one('iframe[src], iframe[data-src], .player-embed iframe, #player iframe')
        if iframe:
            iframe_url = iframe.get('src') or iframe.get('data-src') or ""
            if iframe_url.startswith('//'): iframe_url = 'https:'+iframe_url
            elif iframe_url.startswith('/'): iframe_url = 'https://anichin.moe'+iframe_url
        if not iframe_url:
            iframe_url = url
    except Exception as e:
        title = f"Player — {url}"
        servers = ["Default"]
        iframe_url = ""
    iframe_proxy = f"/api/proxy-player?url={quote(iframe_url, safe='')}" if iframe_url else ""
    user = get_current_user()
    return render_template('player.html', title=title, iframe_url=iframe_url, iframe_proxy=iframe_proxy, servers=servers if servers else ["Default","Okru","StreamWish"], clean_url=clean_url, current_server=server or (servers[0] if servers else "Default"), user=user, original_url=url)

@app.route("/stream")
def stream():
    query = request.args.get('q')
    server = request.args.get('server', 'Okru')
    if not query:
        return "Query tidak boleh kosong!", 400
    target_url = resolve_episode_url(query)
    if not target_url:
        return "Episode tidak ditemukan!", 404
    try:
        res_page = requests.get(target_url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(res_page.text, 'html.parser')
        title_el = soup.select_one('h1.entry-title, .post-title h1, h1')
        title = title_el.text.strip() if title_el else "Streaming Video"
    except Exception:
        title = "Streaming Video"
        target_url = target_url or query
    try:
        iframe_url = asyncio.run(scrape_iframe_async(target_url, server))
    except Exception:
        iframe_url = None
    if not iframe_url:
        return "Gagal mendapatkan URL Iframe dari server tersebut.", 500
    iframe_proxy = f"/api/proxy-player?url={quote(iframe_url, safe='')}"
    user = get_current_user()
    return render_template("player.html", title=title, iframe_url=iframe_url, iframe_proxy=iframe_proxy, servers=[server], clean_url=target_url, current_server=server, user=user, original_url=target_url, server_name=server)

# ---------- Proxy Anti-403 ----------
def rewrite_html_for_proxy(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    # Inject referrer spoof + base
    head = soup.find('head')
    if head is not None:
        spoof = soup.new_tag('script')
        spoof.string = "try{Object.defineProperty(document,'referrer',{get:()=>'https://anichin.moe/'});}catch(e){} try{history.replaceState(null,'','https://anichin.moe/');}catch(e){}"
        head.insert(0, spoof)
        base = soup.new_tag('base', href=base_url)
        head.insert(0, base)
    # Rewrite all src/href to go via proxy
    for tag in soup.find_all(attrs={'src': True}):
        src = tag['src']
        if src.startswith('http') or src.startswith('//'):
            tag['src'] = f"/api/proxy-player?url={quote(src, safe='')}"
        elif src.startswith('/'):
            tag['src'] = f"/api/proxy-player?url={quote(urljoin(base_url, src), safe='')}"
    for tag in soup.find_all(attrs={'href': True}):
        href = tag['href']
        if href.startswith('http') or href.startswith('//'):
            # only proxy html/video/m3u8, not external css? proxy all for safety but keep same
            if any(x in href for x in ['.m3u8','.mp4','.ts','.js','.css','.png','.jpg','.webp']):
                tag['href'] = f"/api/proxy-player?url={quote(href, safe='')}"
    return str(soup)

def rewrite_m3u8(content, base_url):
    lines=[]
    for line in content.splitlines():
        line=line.strip()
        if not line or line.startswith('#'):
            # keep tags, but rewrite URI in EXT-X-KEY etc
            m = re.search(r'URI="([^"]+)"', line)
            if m:
                orig=m.group(1)
                prox=f"/api/proxy-player?url={quote(urljoin(base_url, orig), safe='')}"
                line=line.replace(orig, prox)
            lines.append(line)
        else:
            # segment url
            full = urljoin(base_url, line)
            prox = f"/api/proxy-player?url={quote(full, safe='')}"
            lines.append(prox)
    return "\n".join(lines)

@app.route('/cdn-cgi/<path:path>', methods=['GET','POST','OPTIONS'])
def cdn_cgi_catchall(path):
    # Cloudflare beacon / challenge - return empty to avoid 404 console errors
    return Response("", status=204, headers={"Access-Control-Allow-Origin":"*"})

@app.route('/api/proxy-player')
def proxy_player():
    target = request.args.get('url') or request.args.get('src') or ""
    if not target:
        return "Missing url", 400
    target = unquote(target)
    # Handle nested anichin-player proxy: https://anichin-player.web.id/api/proxy-player?url=https://...
    if "anichin-player.web.id/api/proxy-player" in target:
        m = re.search(r'[?&]url=([^&]+)', target)
        if m:
            target = unquote(m.group(1))
    # Blacklist: beacon, cdn-cgi, cloudflareinsights, chrome-extension, invalid
    blacklist = ["cdn-cgi", "beacon.min.js", "cloudflareinsights", "cdn-cgi/challenge", "rum?", "chrome-extension://", "chrome-extension:invalid", "dick@2x.png", "dick_hov@2x.png"]
    if any(b in target for b in blacklist):
        return Response("", status=204, headers={"Access-Control-Allow-Origin":"*"})
    if target.startswith('//'):
        target = 'https:' + target
    elif target.startswith('/'):
        target = 'https://anichin.moe' + target
    if not target.startswith('http'):
        return "Invalid url", 400
    # Block chrome-extension invalid
    if target.startswith("chrome-extension://"):
        return Response("", status=204)
    try:
        proxy_headers = {
            "User-Agent": HEADERS["User-Agent"],
            "Referer": "https://anichin.moe/",
            "Origin": "https://anichin.moe",
            "Accept": request.headers.get("Accept", "*/*"),
            "Accept-Language": request.headers.get("Accept-Language", "en-US,en;q=0.9"),
            "Accept-Encoding": "identity",
        }
        if "Range" in request.headers:
            proxy_headers["Range"] = request.headers["Range"]
        r = requests.get(target, headers=proxy_headers, stream=True, timeout=15, allow_redirects=True)
        excluded = {'content-encoding','content-length','transfer-encoding','connection','x-frame-options','content-security-policy','content-security-policy-report-only','x-content-type-options','x-xss-protection'}
        resp_headers = {}
        for k, v in r.headers.items():
            if k.lower() not in excluded:
                resp_headers[k] = v
        resp_headers['Access-Control-Allow-Origin'] = '*'
        resp_headers['Access-Control-Allow-Headers'] = '*'
        resp_headers['Access-Control-Expose-Headers'] = '*'
        resp_headers['X-Frame-Options'] = 'ALLOWALL'
        resp_headers['Content-Security-Policy'] = "frame-ancestors *"
        content_type = r.headers.get('Content-Type','')
        # m3u8 rewrite
        if 'mpegurl' in content_type or target.endswith('.m3u8'):
            text = r.text
            rewritten = rewrite_m3u8(text, target)
            return Response(rewritten, status=r.status_code, headers=resp_headers, content_type='application/vnd.apple.mpegurl')
        if 'text/html' in content_type:
            text = r.text
            text = re.sub(r'<meta[^>]*http-equiv=["\']Content-Security-Policy["\'][^>]*>', '', text, flags=re.IGNORECASE)
            # rewrite html to proxy subresources
            try:
                text = rewrite_html_for_proxy(text, target)
            except Exception:
                pass
            return Response(text, status=r.status_code, headers=resp_headers, content_type='text/html; charset=utf-8')
        def generate():
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        return Response(stream_with_context(generate()), status=r.status_code, headers=resp_headers, direct_passthrough=False)
    except Exception as e:
        return f"Proxy error: {e}", 502

@app.route('/proxy-stream')
def proxy_stream():
    target_url = request.args.get('url')
    if not target_url:
        return "URL tidak valid", 400
    # Handle nested proxy from anichin-player
    if "anichin-player.web.id/api/proxy-player" in target_url:
        m = re.search(r'[?&]url=([^&]+)', target_url)
        if m:
            target_url = unquote(m.group(1))
    # Blacklist beacon/cdn-cgi
    if any(x in target_url for x in ["cdn-cgi", "beacon.min.js", "cloudflareinsights", "chrome-extension://"]):
        return Response("", status=204)
    try:
        resp = requests.get(target_url, headers=HEADERS, timeout=10)
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection', 'content-security-policy', 'x-frame-options', 'x-content-type-options']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        # Add CORS for iframe
        headers.append(('Access-Control-Allow-Origin', '*'))
        headers.append(('X-Frame-Options', 'ALLOWALL'))
        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        return f"Proxy Error: {str(e)}", 500

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------- Auth APIs ----------
@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or request.form
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    if not username or not email or not password:
        return jsonify({"status":"error","message":"Semua field wajib diisi"}), 400
    if len(password) < 6:
        return jsonify({"status":"error","message":"Password minimal 6 karakter"}), 400
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return jsonify({"status":"error","message":"Email tidak valid"}), 400
    conn = get_db()
    if conn.execute('SELECT id FROM users WHERE username=?', (username,)).fetchone():
        conn.close(); return jsonify({"status":"error","message":"Username sudah dipakai"}), 400
    if conn.execute('SELECT id FROM users WHERE email=?', (email,)).fetchone():
        conn.close(); return jsonify({"status":"error","message":"Email sudah terdaftar"}), 400
    pwd_hash = generate_password_hash(password)
    cur = conn.execute('INSERT INTO users (username,email,password_hash) VALUES (?,?,?)', (username,email,pwd_hash))
    conn.commit()
    uid = cur.lastrowid
    conn.close()
    session.permanent = True
    session['user_id']=uid
    session['username']=username
    return jsonify({"status":"success","message":"Registrasi berhasil","user":{"id":uid,"username":username,"email":email}})

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or request.form
    ident = (data.get('username') or data.get('email') or '').strip()
    password = data.get('password') or ''
    if not ident or not password:
        return jsonify({"status":"error","message":"Username/email & password wajib"}),400
    conn = get_db()
    row = conn.execute('SELECT * FROM users WHERE username=? OR email=?', (ident.lower(), ident.lower())).fetchone()
    if not row:
        row = conn.execute('SELECT * FROM users WHERE username=? OR email=?', (ident, ident)).fetchone()
    conn.close()
    if not row or not row['password_hash'] or not check_password_hash(row['password_hash'], password):
        return jsonify({"status":"error","message":"Kredensial salah"}),401
    session.permanent = True
    session['user_id']=row['id']
    session['username']=row['username']
    return jsonify({"status":"success","message":"Login berhasil","user":{"id":row['id'],"username":row['username'],"email":row['email'],"avatar":row['avatar']}})

@app.route('/api/auth/google', methods=['POST'])
def api_google():
    data = request.get_json()
    if not data: return jsonify({"status":"error","message":"No data"}),400
    email = (data.get('email') or '').strip().lower()
    name = (data.get('name') or data.get('username') or '').strip()
    picture = data.get('picture') or data.get('avatar') or ''
    google_id = data.get('sub') or data.get('google_id') or ''
    credential = data.get('credential') or ''

    if credential:
        # Try to verify with google-auth library first
        if HAS_GOOGLE_AUTH and GOOGLE_CLIENT_ID and GOOGLE_CLIENT_ID != 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com':
            try:
                idinfo = id_token.verify_oauth2_token(credential, google.auth.transport.requests.Request(), GOOGLE_CLIENT_ID)
                email = idinfo.get('email', '').lower()
                name = name or idinfo.get('name', '') or idinfo.get('given_name', '')
                picture = picture or idinfo.get('picture', '')
                google_id = idinfo.get('sub', '')
            except Exception:
                pass

        # Fallback: decode JWT manually (not cryptographically verified)
        if not email:
            try:
                payload = credential.split('.')[1]
                padding = '=' * (-len(payload) % 4)
                decoded = base64.urlsafe_b64decode(payload + padding)
                obj = json.loads(decoded)
                email = obj.get('email', '').lower()
                name = name or obj.get('name') or obj.get('given_name', '')
                picture = picture or obj.get('picture', '')
                google_id = google_id or obj.get('sub', '')
            except Exception as e:
                return jsonify({"status": "error", "message": f"Gagal verifikasi Google: {e}"}), 400

    if not email:
        return jsonify({"status": "error", "message": "Email Google tidak ditemukan"}), 400

    if not name:
        name = email.split('@')[0]

    base_username = re.sub(r'[^a-zA-Z0-9_]', '', name.replace(' ', '_'))[:20] or email.split('@')[0]
    conn = get_db()
    row = conn.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
    if row:
        if not row['google_id'] and google_id:
            conn.execute('UPDATE users SET google_id=?, avatar=COALESCE(avatar,?) WHERE id=?', (google_id, picture, row['id']))
            conn.commit()
        uid = row['id']
        username = row['username']
    else:
        username = base_username
        i = 1
        while conn.execute('SELECT id FROM users WHERE username=?', (username,)).fetchone():
            username = f"{base_username}{i}"
            i += 1
        cur = conn.execute('INSERT INTO users (username, email, google_id, avatar) VALUES (?, ?, ?, ?)',
                           (username, email, google_id, picture))
        conn.commit()
        uid = cur.lastrowid
    conn.close()
    conn.close()
    session.permanent = True
    session['user_id'] = uid
    session['username'] = username
    return jsonify({"status": "success", "message": "Login Google berhasil", "user": {"id": uid, "username": username, "email": email, "avatar": picture}})

@app.route('/api/auth/me')
def api_me():
    user = get_current_user()
    if not user: return jsonify({"logged_in":False}), 401
    return jsonify({"logged_in":True,"user":{"id":user['id'],"username":user['username'],"email":user['email'],"avatar":user['avatar']}})

@app.route('/api/auth/logout', methods=['POST','GET'])
def api_logout():
    session.clear()
    return jsonify({"status":"success","message":"Logout berhasil"})

def send_whatsapp_otp(phone, otp):
    """Send OTP via Fonnte WhatsApp API"""
    if not FONNTE_TOKEN:
        print(f"[OTP] {phone} -> {otp} (No Fonnte token, console only)")
        return False

    # Normalize phone: remove spaces, dashes, dots, leading +
    clean = re.sub(r'[\s\-\.\(\)\+]', '', phone)
    # Add country code 62 if starts with 0
    if clean.startswith('0'):
        clean = '62' + clean[1:]

    msg = f"*VEXORA*\n\nKode login kamu: *{otp}\n\nJangan bagikan kode ini ke siapapun. Berlaku 5 menit."

    try:
        resp = requests.post(
            'https://api.fonnte.com/send',
            headers={'Authorization': FONNTE_TOKEN},
            data={'target': clean, 'message': msg, 'delay': '2'},
            timeout=10
        )
        result = resp.json()
        print(f"[WA] {phone} -> {result}")
        return result.get('status') == True
    except Exception as e:
        print(f"[WA ERROR] {e}")
        return False

@app.route('/api/auth/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    phone = (data.get('phone') or '').strip()
    # Normalize: remove spaces, dashes, dots
    phone = re.sub(r'[\s\-\.\(\)]', '', phone)
    if not phone:
        return jsonify({"status": "error", "message": "Nomor telepon wajib diisi"}), 400
    # Generate 6-digit OTP
    otp = f"{secrets.randbelow(900000) + 100000}"
    # Store OTP with 5-minute expiry
    otp_store[phone] = {"otp": otp, "expires": time.time() + 300}

    # Send via WhatsApp Fonnte
    sent = send_whatsapp_otp(phone, otp)

    if sent:
        message = "Kode OTP telah dikirim ke WhatsApp kamu"
    else:
        message = f"Kode OTP: {otp} (mode dev — belum ada token Fonnte)"

    resp_data = {"status": "success", "message": message}
    if not FONNTE_TOKEN:
        resp_data["otp"] = otp  # Dev fallback
    return jsonify(resp_data)

@app.route('/api/auth/verify-phone', methods=['POST'])
def verify_phone():
    data = request.get_json()
    phone = (data.get('phone') or '').strip()
    phone = re.sub(r'[\s\-\.\(\)]', '', phone)
    otp_input = (data.get('otp') or '').strip()
    if not phone or not otp_input:
        return jsonify({"status": "error", "message": "Nomor telepon dan OTP wajib diisi"}), 400

    stored = otp_store.get(phone)
    if not stored or stored['otp'] != otp_input:
        return jsonify({"status": "error", "message": "OTP salah atau sudah kedaluwarsa"}), 401
    if time.time() > stored['expires']:
        del otp_store[phone]
        return jsonify({"status": "error", "message": "OTP sudah kedaluwarsa"}), 401

    del otp_store[phone]

    conn = get_db()
    row = conn.execute('SELECT * FROM users WHERE phone=?', (phone,)).fetchone()
    if row:
        uid = row['id']
        username = row['username']
    else:
        # Use provided username (from register form) or generate one
        username = (data.get('username') or '').strip() or f"user_{phone[-4:]}"
        i = 1
        while conn.execute('SELECT id FROM users WHERE username=?', (username,)).fetchone():
            username = f"{username}_{i}"
            i += 1
        cur = conn.execute('INSERT INTO users (username, phone) VALUES (?, ?)', (username, phone))
        conn.commit()
        uid = cur.lastrowid
    conn.close()
    session.permanent = True
    session['user_id'] = uid
    session['username'] = username
    return jsonify({"status": "success", "message": "Login berhasil", "user": {"id": uid, "username": username, "phone": phone}})

@app.route('/api/auth/update-profile', methods=['POST'])
@login_required
def api_update_profile():
    user = get_current_user()
    data = request.get_json() or request.form
    new_username = (data.get('username') or '').strip()
    new_email = (data.get('email') or '').strip().lower()
    if new_username and new_username != user['username']:
        conn=get_db()
        if conn.execute('SELECT id FROM users WHERE username=? AND id!=?', (new_username,user['id'])).fetchone():
            conn.close(); return jsonify({"status":"error","message":"Username sudah dipakai"}),400
        conn.execute('UPDATE users SET username=? WHERE id=?', (new_username,user['id']))
        conn.commit(); conn.close()
        session['username']=new_username
    if new_email and new_email != user['email']:
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', new_email):
            return jsonify({"status":"error","message":"Email tidak valid"}),400
        conn=get_db()
        if conn.execute('SELECT id FROM users WHERE email=? AND id!=?', (new_email,user['id'])).fetchone():
            conn.close(); return jsonify({"status":"error","message":"Email sudah dipakai"}),400
        conn.execute('UPDATE users SET email=? WHERE id=?', (new_email,user['id']))
        conn.commit(); conn.close()
    return jsonify({"status":"success","message":"Profile diperbarui"})

@app.route('/api/auth/upload-avatar', methods=['POST'])
@login_required
def api_upload_avatar():
    if 'avatar' not in request.files:
        return jsonify({"status":"error","message":"File tidak ditemukan"}),400
    f=request.files['avatar']
    if f.filename=='' or not allowed_file(f.filename):
        return jsonify({"status":"error","message":"Format harus png/jpg/jpeg/webp/gif"}),400
    ext=f.filename.rsplit('.',1)[1].lower()
    filename=f"avatar_{session['user_id']}_{secrets.token_hex(4)}.{ext}"
    path=os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    f.save(path)
    rel=f"/static/uploads/{filename}"
    conn=get_db()
    conn.execute('UPDATE users SET avatar=? WHERE id=?', (rel, session['user_id']))
    conn.commit(); conn.close()
    return jsonify({"status":"success","message":"Avatar diperbarui","avatar":rel})

# ---------- Scrape APIs with fallback ----------
@app.route('/api/detail-data', methods=['GET'])
def api_detail_data():
    target_url = request.args.get('url')
    if not target_url:
        return jsonify({"status": "error", "message": "URL parameter is missing"}), 400
    try:
        response = requests.get(target_url, headers=HEADERS, timeout=12)
        if response.status_code != 200:
            return jsonify({"status": "error", "statusCode": response.status_code}), response.status_code
        soup = BeautifulSoup(response.text, 'html.parser')
        title_elem = soup.select_one('h1.entry-title, .infox h1, .post-title')
        title = title_elem.text.strip() if title_elem else "Detail Vexora"
        synopsis_elem = soup.select_one('.entry-content, .desc, .synopsis, [itemprop="description"], div.bixbox.synp')
        synopsis = synopsis_elem.text.strip() if synopsis_elem else "Tidak ada sinopsis tersedia."
        poster_elem = soup.select_one('.thumb img, .infox .fotoimg img, .poster img')
        poster = poster_elem.get('src') or poster_elem.get('data-src') if poster_elem else ""
        genres=[]
        genre_container = soup.select('.genxinf, .genre-info, .spe')
        for container in genre_container:
            for g in container.select('a[href*="/genres/"]'):
                g_text=g.text.strip()
                if g_text and g_text not in genres: genres.append(g_text)
        if not genres:
            for g in soup.select('a[rel="tag"]'):
                g_text=g.text.strip()
                if g_text and g_text not in genres: genres.append(g_text)
        meta_data={}
        for row in soup.select('.info-content .spe span, .infox .spe span'):
            text=row.text.strip()
            if ':' in text:
                k,v=text.split(':',1)
                meta_data[k.strip().lower()]=v.strip()
        episodes=[]
        for ep in soup.select('.eplister ul li a, .episodelist ul li a'):
            ep_title=ep.select_one('.epl-title')
            ep_num=ep.select_one('.epl-num')
            ep_url=ep.get('href')
            if ep_url:
                if not ep_url.startswith("http"): ep_url=f"https://anichin.moe{ep_url}"
                local_player_url = f"/player?url={ep_url}"
                episodes.append({"title":ep_title.text.strip() if ep_title else "Episode","number":ep_num.text.strip() if ep_num else "Ep","url":local_player_url,"original_url":ep_url})
        return jsonify({"status":"success","title":title,"synopsis":synopsis,"poster":poster,"genres":genres,"meta":meta_data,"episodes":episodes})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}),500

@app.route('/api/home', methods=['GET'])
def api_home():
    target_url="https://anichin.moe/"
    t_start=time.time()
    try:
        response=requests.get(target_url, headers=HEADERS, timeout=12)
        elapsed=round(time.time()-t_start,2)
        if response.status_code!=200:
            # inject more_url ke mock biar frontend tetap ada tombol Selanjutnya
            mock_with_more=[]
            for sec in MOCK_SECTIONS:
                s=dict(sec)
                s["more_url"]="/page/2"
                s["archive_url"]="https://anichin.moe/page/2/"
                mock_with_more.append(s)
            return jsonify({"creator":"Vexalyn Developer","statusCode":200,"status":"success","elapsed_time":f"{elapsed} seconds","fallback":True,"sections":mock_with_more})
        soup=BeautifulSoup(response.text,'html.parser')
        sections=[]
        block_elements=soup.select('.releases, .section, .widget, .bixbox, div[class*="venz"], div[class*="listupd"]')
        for block in block_elements:
            header_tag=block.select_one('h2, h3, h4, .hport span, .releases h2, .widget-title')
            if header_tag:
                section_title=header_tag.text.strip()
                if re.search(r'Episode\s+\d+|Subtitle\s+Indonesia', section_title, re.IGNORECASE): continue
                items=parse_anime_items(block)
                if items:
                    # deteksi link Selanjutnya / arsip section
                    more_url=None
                    # 1) cari a.next / pagination
                    cand = block.select_one('a.next, a[rel="next"], .pagination a.next, .nav-links a.next, a.loadmore, a.more')
                    if cand and cand.get('href'):
                        more_url=cand.get('href')
                    else:
                        # 2) cari link teks Selanjutnya/Selengkapnya/Lihat Semua di dalam block
                        for a in block.select('a'):
                            txt=(a.get_text() or "").strip().lower()
                            if txt in ["selanjutnya","selanjutnya >","selengkapnya","lihat semua","more","next"] or "selanjutnya" in txt or "selengkapnya" in txt:
                                if a.get('href'):
                                    more_url=a.get('href'); break
                    # 3) fallback: cari pagination global di block
                    if not more_url:
                        pag = block.select_one('.pagination a[href*="/page/"], .nav-links a[href*="/page/"]')
                        if pag and pag.get('href'): more_url=pag.get('href')
                    # 4) fallback: header link (judul section biasanya link ke arsip)
                    if not more_url:
                        hl = header_tag if header_tag.name=='a' else header_tag.find_parent('a') or block.select_one('h2 a, h3 a, .widget-title a')
                        if hl and hl.get('href'): more_url=hl.get('href')
                    if more_url and not more_url.startswith("http"):
                        more_url=urljoin("https://anichin.moe/", more_url)
                    # selalu beri fallback biar tombol Selanjutnya > muncul
                    if not more_url:
                        # coba tebak arsip dari judul section
                        low=section_title.lower()
                        if "drop" in low: more_url="https://anichin.moe/drop/"
                        elif "rilis" in low or "update" in low or "terbaru" in low: more_url="https://anichin.moe/page/2/"
                        elif "ongoing" in low: more_url="https://anichin.moe/ongoing/"
                        else: more_url="https://anichin.moe/page/2/"
                    sections.append({"section_name":section_title,"total_items":len(items),"data":items,"more_url":more_url,"archive_url":more_url})
        if not sections:
            mock_with_more=[]
            for sec in MOCK_SECTIONS:
                s=dict(sec); s["more_url"]="/page/2"; s["archive_url"]="https://anichin.moe/page/2/"; mock_with_more.append(s)
            return jsonify({"creator":"Vexalyn Developer","statusCode":200,"status":"success","elapsed_time":f"{elapsed} seconds","fallback":True,"sections":mock_with_more})
        return jsonify({"creator":"Vexalyn Developer","statusCode":200,"status":"success","elapsed_time":f"{elapsed} seconds","sections":sections})
    except Exception as e:
        mock_with_more=[]
        for sec in MOCK_SECTIONS:
            s=dict(sec); s["more_url"]="/page/2"; s["archive_url"]="https://anichin.moe/page/2/"; mock_with_more.append(s)
        return jsonify({"creator":"Vexalyn Developer","statusCode":200,"status":"success","elapsed_time":"0 seconds","fallback":True,"sections":mock_with_more,"error":str(e)})

@app.route('/api/load-more', methods=['GET'])
def api_load_more():
    target_url=request.args.get('url') or request.args.get('archive') or ""
    if not target_url:
        return jsonify({"status":"error","message":"Parameter url wajib (archive/halaman section)"}),400
    target_url=unquote(target_url)
    if target_url.startswith('/'):
        target_url=urljoin("https://anichin.moe/", target_url)
    if not target_url.startswith('http'):
        target_url="https://anichin.moe/"+target_url.lstrip('/')
    t_start=time.time()
    try:
        r=requests.get(target_url, headers=HEADERS, timeout=12)
        elapsed=round(time.time()-t_start,2)
        if r.status_code!=200:
            return jsonify({"status":"error","message":f"Gagal load {r.status_code}"}),r.status_code
        soup=BeautifulSoup(r.text,'html.parser')
        # ambil items dari halaman arsip
        items=parse_anime_items(soup)
        # jika kosong, coba cari block spesifik
        if not items:
            for block in soup.select('.releases, .listupd, .bixbox'):
                items=parse_anime_items(block)
                if items: break
        # cari next page
        next_url=None
        nxt=soup.select_one('a.next, a[rel="next"], .pagination a.next, .nav-links a.next, a[href*="/page/"]')
        # cari yang href beda dari current dan mengandung page
        if not nxt:
            for a in soup.select('.pagination a, .nav-links a'):
                href=a.get('href') or ""
                if "/page/" in href and href!=target_url:
                    nxt=a; break
        if nxt and nxt.get('href'):
            next_url=nxt.get('href')
            if not next_url.startswith('http'): next_url=urljoin(target_url, next_url)
        # fallback next: increment page number
        if not next_url and "/page/" in target_url:
            m=re.search(r'/page/(\d+)', target_url)
            if m:
                n=int(m.group(1))+1
                next_url=re.sub(r'/page/\d+', f'/page/{n}', target_url)
            else:
                next_url=urljoin(target_url.rstrip('/')+'/', 'page/2/')
        elif not next_url:
            # kalau url tanpa page, next adalah page/2
            next_url=urljoin(target_url.rstrip('/')+'/', 'page/2/')
        # jika items masih kosong, pakai mock
        if not items:
            items=MOCK_SECTIONS[0]["data"][:6]
        return jsonify({"creator":"Vexalyn Developer","statusCode":200,"status":"success","elapsed_time":f"{elapsed} seconds","url":target_url,"next_url":next_url,"more_url":next_url,"total_items":len(items),"data":items})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}),500

@app.route('/api/banner', methods=['GET'])
def api_banner():
    t_start=time.time()
    banners=scrape_banner_data()
    elapsed=round(time.time()-t_start,2)
    return jsonify({"creator":"Vexalyn Developer","statusCode":200,"status":"success","elapsed_time":f"{elapsed} seconds","total_banners":len(banners),"banners":banners})

@app.route('/api/schedule', methods=['GET'])
def api_schedule():
    t_start=time.time()
    data=scrape_schedule_data()
    elapsed=round(time.time()-t_start,2)
    return jsonify({"creator":"Vexalyn Developer","statusCode":200,"status":"success","elapsed_time":f"{elapsed} seconds","total_days":len(data),"schedule":data})

@app.route('/api/genres', methods=['GET'])
def api_all_genres():
    FALLBACK_GENRES = [{"name":n,"slug":s} for n,s in [
        ("Action","action"),("Adventure","adventure"),("Cultivation","cultivation"),("Fantasy","fantasy"),
        ("Martial Arts","martial-arts"),("Romance","romance"),("Comedy","comedy"),("Drama","drama"),
        ("Historical","historical"),("Supernatural","supernatural"),("Sci-Fi","sci-fi"),("Reincarnation","reincarnation"),
        ("Harem","harem"),("Demons","demons"),("Magic","magic"),("Mystery","mystery")
    ]]
    target_url="https://anichin.moe/genres/"
    try:
        response=requests.get(target_url, headers=HEADERS, timeout=12)
        if response.status_code!=200:
            return jsonify({"status":"success","total":len(FALLBACK_GENRES),"data":FALLBACK_GENRES,"fallback":True})
        soup=BeautifulSoup(response.text,'html.parser')
        genre_elements=soup.select('a[href*="/genres/"], a[href*="/genre/"], .genres a, .genre-list a, .tagcloud a')
        genres_list=[]; seen=set()
        for el in genre_elements:
            raw_name=el.text.strip(); href=el.get('href','') or ''
            m=re.search(r'/genres?/([^/?#]+)/?', href)
            if m:
                slug=m.group(1).lower().strip()
                if slug and slug not in seen and raw_name and not slug.isdigit() and len(slug)>1 and len(slug)<30:
                    if re.match(r'^[a-z0-9-]+$', slug):
                        seen.add(slug)
                        clean_name=re.sub(r'\s*\(\d+\)$','',raw_name).strip()
                        clean_name=re.sub(r'\s+\d+$','',clean_name).strip()
                        if clean_name and not clean_name.isdigit():
                            genres_list.append({"name":clean_name,"slug":slug})
        if len(genres_list) < 6:
            return jsonify({"status":"success","total":len(FALLBACK_GENRES),"data":FALLBACK_GENRES,"fallback":True, "scraped":len(genres_list)})
        return jsonify({"status":"success","total":len(genres_list),"data":genres_list})
    except Exception as e:
        return jsonify({"status":"success","total":len(FALLBACK_GENRES),"data":FALLBACK_GENRES,"fallback":True,"error":str(e)})

@app.route('/api/genre/<path:genre_slug>', methods=['GET'])
def api_genre(genre_slug):
    clean_genre=genre_slug.strip().lower().replace(" ","-")
    target_url=f"https://anichin.moe/genres/{clean_genre}/"
    t_start=time.time()
    try:
        response=requests.get(target_url, headers=HEADERS, timeout=12)
        elapsed=round(time.time()-t_start,2)
        if response.status_code!=200:
            filtered=[]
            for sec in MOCK_SECTIONS:
                for item in sec["data"]:
                    if clean_genre in item["title"].lower() or True:
                        filtered.append(item)
                    if len(filtered)>=12: break
            return jsonify({"creator":"Vexalyn Developer","statusCode":200,"status":"success","genre":clean_genre,"elapsed_time":f"{elapsed} seconds","fallback":True,"total_data":len(filtered[:12]),"data":filtered[:12]})
        soup=BeautifulSoup(response.text,'html.parser')
        anime_list=parse_anime_items(soup)
        if not anime_list:
            anime_list=MOCK_SECTIONS[0]["data"]
        return jsonify({"creator":"Vexalyn Developer","statusCode":200,"status":"success","genre":clean_genre,"elapsed_time":f"{elapsed} seconds","total_data":len(anime_list),"data":anime_list})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}),500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
