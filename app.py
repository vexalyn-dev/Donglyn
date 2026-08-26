# app.py — Netflix + Auth + Fallback + Proxy Anti-403 + Banner + Schedule
import sys, asyncio, urllib.parse, mimetypes, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, jsonify, request, render_template, render_template_string, redirect, url_for, session, send_from_directory, Response, stream_with_context
import time, re, requests, os, sqlite3, secrets, json, base64, platform, shutil, html
from datetime import datetime
from urllib.parse import quote, unquote, urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv(override=True)

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
try:
    import brotli
except ImportError:
    brotli = None
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from flask_limiter import Limiter  # type: ignore
from flask_limiter.util import get_remote_address  # type: ignore

try:
    import resend  # type: ignore
    HAS_RESEND = True
except ImportError:
    HAS_RESEND = False

try:
    from supabase import create_client, Client  # type: ignore
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config['UPLOAD_FOLDER'] = os.path.join('static','uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 30

# Rate Limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# CSRF token helpers
import string as _string
def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']

def validate_csrf_token():
    token = request.headers.get('X-CSRF-Token') or (request.get_json(silent=True) or {}).get('_csrf_token')
    if not token or token != session.get('_csrf_token'):
        return False
    return True

app.jinja_env.globals['csrf_token'] = generate_csrf_token
ALLOWED_EXT = {'png','jpg','jpeg','webp','gif'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
APP_START_TIME = time.time()
DEV_SECRET_KEY = os.environ.get('DEV_SECRET_KEY', 'VEXORA_DEV_SECRET_2026')
DEV_PANEL_ADMINS = {name.strip().lower() for name in os.environ.get('DEV_PANEL_ADMINS', 'admin,vexora,developer,devpanel').split(',') if name.strip()}
_dev_logs = []
_supabase_dev_logs_available = None


def add_dev_log(message, level='INFO', category='system'):
    entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'level': level.upper(),
        'category': category,
        'message': str(message),
    }
    _dev_logs.append(entry)
    if len(_dev_logs) > 250:
        _dev_logs.pop(0)
    if (globals().get('USE_SUPABASE') and globals().get('supabase') is not None
            and globals().get('_supabase_dev_logs_available') is not False):
        try:
            supabase.table('dev_logs').insert({
                'level': entry['level'],
                'category': entry['category'],
                'message': entry['message'],
            }).execute()
            globals()['_supabase_dev_logs_available'] = True
        except Exception as exc:
            if 'PGRST205' in str(exc):
                globals()['_supabase_dev_logs_available'] = False
            else:
                print(f"[DEV LOG PERSISTENCE ERROR] {exc}")
    print(f"[DEV::{category}::{level}] {message}")


add_dev_log('Dev panel helper initialized', 'INFO', 'startup')

# ---------- Caching ----------
try:
    from flask_caching import Cache  # type: ignore
    HAS_CACHE = True
except ImportError:
    HAS_CACHE = False

CACHE_TTL = int(os.environ.get("CACHE_TTL", "600"))  # default 10 minutes

if HAS_CACHE:
    app.config["CACHE_TYPE"] = "SimpleCache"
    app.config["CACHE_DEFAULT_TIMEOUT"] = CACHE_TTL
    cache = Cache(app)
    print(f"[CACHE] Flask-Caching enabled (SimpleCache, TTL={CACHE_TTL}s)")
else:
    cache = None
    print("[CACHE] Flask-Caching not available, using manual fallback")

# Manual fallback cache (used only if flask_caching is missing)
_manual_cache = {}
DB_CACHE_TTL = 180
_db_cache_refreshing = set()
_db_cache_lock = threading.Lock()

def _extract_json(fn, *args, **kwargs):
    """Run a view and return its payload as a plain JSON-serializable object."""
    resp = fn(*args, **kwargs)
    if hasattr(resp, 'get_json'):
        data = resp.get_json()
        if data is not None:
            return data
    try:
        return json.loads(resp.get_data(as_text=True))
    except Exception:
        return resp

def cached_route(timeout=None):
    """Cache a GET view using the SQLite/Supabase `cache` table.

    The table stores the payload as a JSON string keyed by `key` (PRIMARY KEY,
    automatically indexed) so read/write stays fast. On a cache hit the payload is
    returned directly; if the entry is stale it is refreshed in the background.
    """
    ttl = timeout or CACHE_TTL
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = "route:" + request.full_path
            cached, stale = read_db_cache(key, ttl)
            if cached is not None:
                if stale:
                    refresh_db_cache_async(key, lambda: _extract_json(fn, *args, **kwargs))
                return jsonify(cached)
            data = _extract_json(fn, *args, **kwargs)
            write_db_cache(key, data)
            return jsonify(data)
        return wrapper
    return decorator

def ensure_cache_table():
    if USE_SUPABASE:
        return
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS cache (
        key TEXT PRIMARY KEY,
        data TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def ensure_dev_logs_table():
    if USE_SUPABASE:
        return
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS dev_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        level TEXT NOT NULL DEFAULT 'INFO',
        category TEXT NOT NULL DEFAULT 'system',
        message TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

def read_db_cache(key, ttl=None):
    ttl = ttl or DB_CACHE_TTL
    if USE_SUPABASE:
        try:
            response = supabase.table('cache').select('data, updated_at').eq('key', key).limit(1).execute()
            row = (response.data or [None])[0]
            if not row:
                return None, True
            data = row.get('data')
            if isinstance(data, str):
                data = json.loads(data)
            updated = datetime.fromisoformat(str(row['updated_at']).replace('Z', '+00:00'))
            age = (datetime.now(updated.tzinfo) - updated).total_seconds()
            return data, age >= ttl
        except Exception as exc:
            add_dev_log(f'Supabase cache read failed ({key}): {exc}', 'ERROR', 'cache')
            return None, True
    ensure_cache_table()
    conn = get_db()
    row = conn.execute('SELECT data, updated_at FROM cache WHERE key=?', (key,)).fetchone()
    conn.close()
    if not row:
        return None, True
    try:
        data = json.loads(row['data'])
        updated = datetime.fromisoformat(str(row['updated_at']).replace('Z', '+00:00'))
        age = (datetime.now() - updated.replace(tzinfo=None)).total_seconds()
        return data, age >= ttl
    except (TypeError, ValueError, json.JSONDecodeError):
        return None, True

def write_db_cache(key, data):
    if USE_SUPABASE:
        supabase.table('cache').upsert({'key': key, 'data': data, 'updated_at': datetime.now().isoformat()}).execute()
        return
    ensure_cache_table()
    conn = get_db()
    conn.execute('''INSERT INTO cache (key, data, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(key) DO UPDATE SET data=excluded.data, updated_at=CURRENT_TIMESTAMP''',
                 (key, json.dumps(data, ensure_ascii=False)))
    conn.commit()
    conn.close()

def read_dev_logs(limit=100):
    limit = max(1, min(limit, 200))
    if USE_SUPABASE and _supabase_dev_logs_available is not False:
        try:
            response = supabase.table('dev_logs').select('timestamp, level, category, message').order('id', desc=True).limit(limit).execute()
            globals()['_supabase_dev_logs_available'] = True
            logs = response.data or []
            return list(reversed(logs))
        except Exception as exc:
            if 'PGRST205' in str(exc):
                globals()['_supabase_dev_logs_available'] = False
            else:
                raise
    if USE_SUPABASE:
        return _dev_logs[-limit:]
    ensure_dev_logs_table()
    conn = get_db()
    rows = conn.execute('SELECT timestamp, level, category, message FROM dev_logs ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return [dict(row) for row in reversed(rows)]

def get_upload_storage_stats():
    total_bytes = 0
    total_files = 0
    for root, _, filenames in os.walk(app.config['UPLOAD_FOLDER']):
        for filename in filenames:
            try:
                total_bytes += os.path.getsize(os.path.join(root, filename))
                total_files += 1
            except OSError:
                pass
    return {'files': total_files, 'bytes': total_bytes}

def get_device_telemetry():
    os_label = platform.platform(aliased=True)
    if os.name == 'nt':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows NT\CurrentVersion') as key:
                product = winreg.QueryValueEx(key, 'ProductName')[0]
                display_version = winreg.QueryValueEx(key, 'DisplayVersion')[0]
                build = winreg.QueryValueEx(key, 'CurrentBuild')[0]
                os_label = f'{product} ({display_version}, build {build})'
        except (FileNotFoundError, OSError, AttributeError):
            pass
    memory_total = 0
    memory_available = 0
    if os.name == 'nt':
        try:
            import ctypes
            class MemoryStatus(ctypes.Structure):
                _fields_ = [('length', ctypes.c_ulong), ('memory_load', ctypes.c_ulong),
                            ('total', ctypes.c_ulonglong), ('available', ctypes.c_ulonglong),
                            ('pagefile_total', ctypes.c_ulonglong), ('pagefile_available', ctypes.c_ulonglong),
                            ('virtual_total', ctypes.c_ulonglong), ('virtual_available', ctypes.c_ulonglong),
                            ('extended', ctypes.c_ulonglong)]
            status = MemoryStatus()
            status.length = ctypes.sizeof(MemoryStatus)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
                memory_total = status.total
                memory_available = status.available
        except (AttributeError, OSError):
            pass
    drives = []
    for drive_letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        drive = f'{drive_letter}:\\'
        if not os.path.exists(drive):
            continue
        try:
            usage = shutil.disk_usage(drive)
            used = usage.total - usage.free
            drives.append({'name': drive_letter, 'used': used, 'total': usage.total,
                           'free': usage.free, 'percent': round((used / usage.total) * 100) if usage.total else 0})
        except OSError:
            pass
    return {
        'hostname': platform.node() or 'unknown-host',
        'os': os_label,
        'architecture': platform.machine() or 'unknown',
        'cpu': os.environ.get('PROCESSOR_IDENTIFIER') or platform.processor() or 'unknown CPU',
        'cpu_count': os.cpu_count() or 0,
        'memory_total': memory_total,
        'memory_available': memory_available,
        'memory_used': max(0, memory_total - memory_available),
        'memory_percent': round(((memory_total - memory_available) / memory_total) * 100) if memory_total else 0,
        'drives': drives,
    }

def refresh_db_cache_async(key, loader):
    with _db_cache_lock:
        if key in _db_cache_refreshing:
            return
        _db_cache_refreshing.add(key)
    def run():
        try:
            write_db_cache(key, loader())
            add_dev_log(f'Database cache refreshed: {key}', 'INFO', 'cache')
        except Exception as exc:
            add_dev_log(f'Database cache refresh failed ({key}): {exc}', 'ERROR', 'cache')
        finally:
            with _db_cache_lock:
                _db_cache_refreshing.discard(key)
    threading.Thread(target=run, name=f'cache-refresh-{key}', daemon=True).start()

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
FONNTE_TOKEN = os.environ.get("FONNTE_TOKEN", "")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
RESEND_FROM_EMAIL = os.environ.get("RESEND_FROM_EMAIL", "onboarding@resend.dev")
if RESEND_API_KEY and HAS_RESEND:
    resend.api_key = RESEND_API_KEY
    print(f"[EMAIL] Resend configured, sender={RESEND_FROM_EMAIL}")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_SERVER_KEY = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY
supabase: Client = None
if HAS_SUPABASE and SUPABASE_URL and SUPABASE_SERVER_KEY and "your-" not in SUPABASE_URL:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVER_KEY)
        print("[SUPABASE] Connected")
    except Exception as e:
        print(f"[SUPABASE ERROR] {e}")
        supabase = None

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

# Search cache: {(query): (timestamp, results)}
_search_cache = {}
SEARCH_CACHE_TTL = 120  # seconds

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
        email_verified INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    try:
        conn.execute("SELECT phone FROM users LIMIT 1")
    except:
        conn.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    try:
        conn.execute("SELECT email_verified FROM users LIMIT 1")
    except:
        conn.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0")
    conn.commit()
    conn.close()

otp_store = {}
email_verify_tokens = {}  # {token: {"user_id": int, "email": str, "expires": float}}
password_reset_tokens = {}  # {token: {"user_id": int, "email": str, "expires": float}}

# Use Supabase if configured, else fallback to SQLite
USE_SUPABASE = supabase is not None

if USE_SUPABASE:
    print("[DB] Using Supabase")
    # Try to create users table in Supabase if it doesn't exist
    try:
        supabase.table("users").select("id").limit(1).execute()
        print("[DB] Supabase 'users' table OK")
    except Exception as e:
        print(f"[DB] Supabase users table check: {e}")
else:
    print("[DB] Using SQLite (Supabase not configured)")
    init_db()

ensure_cache_table()
ensure_dev_logs_table()

def get_current_user():
    uid = session.get('user_id')
    if not uid: return None
    if USE_SUPABASE:
        try:
            res = supabase.table("users").select("*").eq("id", uid).limit(1).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            print(f"[DB] get_current_user error: {e}")
            return None
    else:
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


def is_dev_admin():
    if session.get('is_admin') is True:
        return True
    user = get_current_user()
    if not user:
        return False
    username = str(user.get('username') or '').strip().lower()
    if username in DEV_PANEL_ADMINS:
        session['is_admin'] = True
        return True
    return False


def dev_panel_required(f):
    @wraps(f)
    def wrap(*a, **kw):
        if not session.get('user_id'):
            if request.path.startswith('/api/'):
                return jsonify({"status": "error", "message": "Login required"}), 401
            return redirect(url_for('login_page'))
        if not is_dev_admin():
            if request.path.startswith('/api/'):
                return jsonify({"status": "error", "message": "Access denied: developer/admin only"}), 403
            return redirect(url_for('index'))
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

@app.route('/search')
def search_page():
    user = get_current_user()
    query = (request.args.get('q') or '').strip()
    return render_template('search.html', user=user, query=query)

@app.route('/detail')
def detail_page():
    target_url = request.args.get('url')
    if not target_url:
        return "URL tidak ditemukan", 400
    user = get_current_user()
    return render_template('detail.html', target_url=target_url, user=user)

@app.route('/login')
def login_page():
    if get_current_user(): return redirect(url_for('index'))
    return render_template('login.html', client_id=GOOGLE_CLIENT_ID)

@app.route('/register')
def register_page():
    if get_current_user(): return redirect(url_for('index'))
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
    episode_match = re.search(r'episode[-/](\d+)', url, re.IGNORECASE)
    episode_label = f"Episode {episode_match.group(1)}" if episode_match else "Episode aktif"
    iframe_url = ""
    servers = []
    episodes = []
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
        if server and server.lower() not in {'default', 'pilih server'}:
            try:
                selected_iframe_url = asyncio.run(scrape_iframe_async(url, server))
                if selected_iframe_url:
                    iframe_url = selected_iframe_url
            except Exception:
                pass
        if not iframe_url:
            iframe_url = url
        for ep in soup.select('.eplister ul li a, .episodelist ul li a'):
            ep_url = ep.get('href')
            if not ep_url:
                continue
            ep_url = urljoin(url, ep_url)
            ep_title = ep.select_one('.epl-title, h3, h2, .playinfo h3')
            ep_text = ep.get_text(' ', strip=True)
            number_match = re.search(r'\b(?:eps?|episode)\s*[-.]?\s*(\d+)\b', ep_text, re.IGNORECASE)
            if not number_match:
                number_match = re.search(r'episode[-_](\d+)', ep_url, re.IGNORECASE)
            episode_number = f"Episode {number_match.group(1)}" if number_match else "Episode"
            episodes.append({
                "title": ep_title.get_text(' ', strip=True) if ep_title else ep_text,
                "number": episode_number,
                "url": ep_url,
                "current": ep_url.rstrip('/') == url.rstrip('/')
            })
        if not episodes:
            episodes = [{"title": title, "number": episode_label, "url": url, "current": True}]
    except Exception as e:
        title = f"Player — {url}"
        servers = ["Default"]
        iframe_url = ""
    iframe_proxy = f"/api/proxy-player?url={quote(iframe_url, safe='')}" if iframe_url else ""
    user = get_current_user()
    return render_template('player.html', title=title, episode_label=episode_label, episodes=episodes, iframe_url=iframe_url, iframe_proxy=iframe_proxy, servers=servers if servers else ["Default","Okru","StreamWish"], clean_url=clean_url, current_server=server or (servers[0] if servers else "Default"), user=user, original_url=url)

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
    episode_match = re.search(r'episode[-/](\d+)', target_url, re.IGNORECASE)
    episode_label = f"Episode {episode_match.group(1)}" if episode_match else "Episode aktif"
    episodes = [{"title": title, "number": episode_label, "url": target_url, "current": True}]
    user = get_current_user()
    return render_template("player.html", title=title, episode_label=episode_label, episodes=episodes, iframe_url=iframe_url, iframe_proxy=iframe_proxy, servers=[server], clean_url=target_url, current_server=server, user=user, original_url=target_url, server_name=server)

# ---------- Proxy Anti-403 ----------
def rewrite_html_for_proxy(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    for iframe in soup.find_all('iframe'):
        iframe.attrs.pop('allowfullscreen', None)
    # Inject referrer spoof + base
    head = soup.find('head')
    if head is not None:
        scrollbar_style = soup.new_tag('style')
        scrollbar_style.string = '''
html, body {
    max-width: 100% !important;
    overflow-x: hidden !important;
    scrollbar-width: none !important;
}
html::-webkit-scrollbar, body::-webkit-scrollbar {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
}
'''
        head.insert(0, scrollbar_style)
        spoof = soup.new_tag('script')
        proxy_origin = f"{urlparse(base_url).scheme}://{urlparse(base_url).netloc}"
        proxy_script = json.dumps("/api/proxy-player?url=")
        spoof.string = """
try{Object.defineProperty(document,'referrer',{get:()=> 'https://anichin.moe/'});}catch(e){}
try{history.replaceState(null,'','/');}catch(e){}
(function(){
    const proxyBase = %s;
    const toProxy = function(value){
        const raw = typeof value === 'string' ? value : (value && value.url) || '';
        if (!raw) return value;
        const absolute = new URL(raw, %s);
        if (!/^\\/web-api(?:\\/|\\?|$)/i.test(absolute.pathname)) return value;
        const target = absolute.href;
        return proxyBase + encodeURIComponent(target);
    };
    const originalFetch = window.fetch;
    window.fetch = function(input, init){
        const rewritten = toProxy(input);
        return originalFetch.call(this, rewritten, init);
    };
    const originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url){
        arguments[1] = toProxy(url);
        return originalOpen.apply(this, arguments);
    };
    const rewriteScript = function(element){
        if (element && element.tagName === 'SCRIPT' && element.src) {
            const rewritten = toProxy(element.src);
            if (rewritten !== element.src) element.src = rewritten;
        }
        return element;
    };
    const originalAppendChild = Node.prototype.appendChild;
    Node.prototype.appendChild = function(element){
        return originalAppendChild.call(this, rewriteScript(element));
    };
    const originalInsertBefore = Node.prototype.insertBefore;
    Node.prototype.insertBefore = function(element, reference){
        return originalInsertBefore.call(this, rewriteScript(element), reference);
    };
})();
""" % (proxy_script, json.dumps(proxy_origin + '/'))
        head.insert(0, spoof)
    # Rewrite all remote resources to the local proxy origin.
    def proxy_resource(resource_url):
        if not resource_url or resource_url.startswith(('data:', 'blob:', 'javascript:', '#')):
            return resource_url
        absolute_url = urljoin(base_url, resource_url)
        return f"/api/proxy-player?url={quote(absolute_url, safe='')}"

    for tag in soup.find_all(attrs={'src': True}):
        src = tag['src']
        tag.attrs.pop('integrity', None)
        tag['src'] = proxy_resource(src)
    for tag in soup.find_all(attrs={'href': True}):
        href = tag['href']
        tag.attrs.pop('integrity', None)
        if href.startswith(('http', '//', '/', './', '../')) or not href.startswith(('#', 'mailto:', 'tel:')):
            tag['href'] = proxy_resource(href)
    rendered = str(soup)

    def rewrite_embedded_web_api(match):
        source_url = match.group(0)
        absolute_url = urljoin(base_url, source_url)
        return f"/api/proxy-player?url={quote(absolute_url, safe='')}"

    rendered = re.sub(
        r"(?<![A-Za-z0-9_])(?:https?:)?//[^\"'\s<>]+/web-api/[^\"'\s<>]*",
        rewrite_embedded_web_api,
        rendered,
        flags=re.IGNORECASE
    )
    return rendered

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

@app.route('/gwtlog', methods=['GET', 'POST', 'OPTIONS'])
def gwtlog_catchall():
    return Response("", status=204, headers={"Access-Control-Allow-Origin":"*"})

def _scrape_search_sync(query):
    """Scrape search results using requests (works with simple sites, bypass cache)."""
    import asyncio as _aio
    try:
        from core.browser import get_page_content
    except ImportError:
        from playwright.sync_api import sync_playwright
        async def _fetch(url):
            async with sync_playwright() as p:
                browser = await p.chromium.launch(headless=True, args=['--no-sandbox','--disable-dev-shm-usage'])
                ctx = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
                page = await ctx.new_page()
                try:
                    await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    await page.wait_for_timeout(3000)
                    html = await page.content()
                finally:
                    await ctx.close()
                    await browser.close()
                return html
        html = _aio.get_event_loop().run_until_complete(_fetch)
    else:
        html = _aio.get_event_loop().run_until_complete(get_page_content(f"https://anichin.moe/?s={urllib.parse.quote(query)}"))
    
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    seen = set()
    items = soup.select('article, .bs, .bsx, .bxy, .listupd, div[class*="item"]')
    if not items:
        items = soup.find_all('a', href=True)
    for item in items:
        try:
            if item.name == 'a':
                a_tag = item
            else:
                a_tag = item.find('a')
            if not a_tag:
                continue
            link = a_tag.get('href', '')
            if not link or not link.startswith('http'):
                link = 'https://anichin.moe' + link if link.startswith('/') else 'https://anichin.moe/' + link
            if link in seen:
                continue
            seen.add(link)
            title = a_tag.get('title') or a_tag.get('alt', '')
            if not title:
                te = a_tag.find(['h2', 'h3', 'div'])
                title = te.text.strip() if te else a_tag.get_text(strip=True)
            if not title:
                continue
            img = item.find('img') if hasattr(item, 'find') else None
            thumb = ''
            if img:
                thumb = img.get('data-lazy-src') or img.get('data-src') or img.get('src', '')
            results.append({'title': title, 'url': link, 'thumbnail': thumb, 'type': '', 'label': ''})
        except Exception:
            continue
    return results

@app.route('/api/search')
def api_search():
    q = (request.args.get('q') or '').strip()
    if not q:
        return jsonify({"status":"error","message":"Masukkan kata kunci pencarian","data":[]}), 400
    # Check cache first
    now = time.time()
    cached = _search_cache.get(q)
    if cached and (now - cached[0]) < SEARCH_CACHE_TTL:
        return jsonify({"status":"success","data":cached[1],"total":len(cached[1])})
    try:
        encoded = urllib.parse.quote(q)
        url = f"https://anichin.moe/?s={encoded}"
        
        # Try Playwright first, fallback to requests
        try:
            import asyncio
            if async_playwright is not None:
                async def _fetch():
                    p = await async_playwright().start()
                    browser = await p.chromium.launch(headless=True, args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu'])
                    ctx = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
                    page = await ctx.new_page()
                    try:
                        await page.goto(url, wait_until='domcontentloaded', timeout=8000)
                        await page.wait_for_timeout(800)
                        html = await page.content()
                    finally:
                        await ctx.close()
                        await p.stop()
                    return html
                html = asyncio.run(_fetch())
            else:
                raise ImportError("playwright not available")
        except Exception:
            resp = requests.get(url, headers=HEADERS, timeout=8)
            html = resp.text
        
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        seen = set()
        items = soup.select('article, .bs, .bsx, .bxy, .listupd, div.utao, div[class*="item"]')
        if not items:
            items = soup.find_all('a', href=True)
        for item in items:
            try:
                if item.name == 'a':
                    a_tag = item
                else:
                    a_tag = item.find('a')
                if not a_tag:
                    continue
                link = a_tag.get('href', '')
                if not link:
                    continue
                if not link.startswith('http'):
                    link = f"https://anichin.moe{link}" if link.startswith('/') else f"https://anichin.moe/{link}"
                if link in seen:
                    continue
                seen.add(link)
                title = a_tag.get('title') or a_tag.get('alt', '')
                if not title:
                    te = item.find(['h2', 'h3', 'div'], class_=lambda c: c and ('tt' in c or 'title' in c))
                    title = te.text.strip() if te else a_tag.get_text(strip=True)
                if not title or len(title) < 2:
                    continue
                img = item.find('img') if hasattr(item, 'find') else None
                thumb = ''
                if img:
                    thumb = img.get('data-lazy-src') or img.get('src') or img.get('data-src', '')
                status_el = item.find(['span', 'div'], class_=lambda c: c and ('epx' in str(c) or 'epi' in str(c) or 'status' in str(c)))
                status = status_el.text.strip() if status_el else ''
                type_el = item.find(['span', 'div'], class_=lambda c: c and 'typez' in c)
                anime_type = type_el.text.strip() if type_el else ''
                results.append({'title': title, 'url': link, 'thumbnail': thumb, 'type': anime_type, 'label': status})
            except Exception:
                continue
        # Cache results
        _search_cache[q] = (now, results)
        return jsonify({"status":"success","data":results,"total":len(results)})
    except Exception as e:
        return jsonify({"status":"error","message":str(e),"data":[]}), 500

@app.route('/api/proxy-player')
def proxy_player():
    target = request.args.get('url') or request.args.get('src') or ""
    if not target:
        return "Missing url", 400
    target = unquote(target)
    # Handle nested anichin-player proxy: https://anichin-player.web.id/api/proxy-player?url=https://...
    if "anichin-player.web.id/api/proxy-player" in target:
        nested_url = parse_qs(urlparse(target).query).get('url', [''])[0]
        if nested_url:
            target = unquote(nested_url)
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
        target_parts = urlparse(target)
        target_host = (target_parts.hostname or '').lower()
        if target_host == 'anichin.moe' or target_host.endswith('.anichin.moe'):
            upstream_referer = 'https://anichin.moe/'
            upstream_origin = 'https://anichin.moe'
        elif target_host == 'ok.ru' or target_host.endswith('.ok.ru'):
            upstream_referer = 'https://ok.ru/'
            upstream_origin = 'https://ok.ru'
        elif (
            target_host == 'vk.com' or target_host.endswith('.vk.com') or
            target_host == 'vk.ru' or target_host.endswith('.vk.ru') or
            '.cdn-vk.' in target_host or target_host.endswith('cdn-vk.ru')
        ):
            upstream_referer = 'https://vk.com/'
            upstream_origin = 'https://vk.com'
        elif target_host and any(
            name in target_host for name in ('streamwish', 'filelions', 'vidhide', 'lulustream')
        ):
            upstream_referer = f'{target_parts.scheme}://{target_host}/'
            upstream_origin = f'{target_parts.scheme}://{target_host}'
        else:
            upstream_referer = f'{target_parts.scheme}://{target_host}/' if target_host else ''
            upstream_origin = f'{target_parts.scheme}://{target_host}' if target_host else ''
        target_path = urlparse(target).path.lower()
        static_mime_types = {
            '.js': 'application/javascript',
            '.mjs': 'application/javascript',
            '.css': 'text/css',
            '.json': 'application/json',
            '.map': 'application/json',
            '.woff': 'font/woff',
            '.woff2': 'font/woff2',
            '.ttf': 'font/ttf',
            '.otf': 'font/otf',
            '.eot': 'application/vnd.ms-fontobject',
        }
        static_extension = next((ext for ext in static_mime_types if target_path.endswith(ext)), None)
        expected_mime = static_mime_types.get(static_extension) if static_extension else None
        proxy_headers = {
            "User-Agent": HEADERS["User-Agent"],
            "Accept": request.headers.get("Accept", "*/*"),
            "Accept-Language": request.headers.get("Accept-Language", "en-US,en;q=0.9"),
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Dest": request.headers.get("Sec-Fetch-Dest", "empty"),
            "Sec-Fetch-Mode": request.headers.get("Sec-Fetch-Mode", "cors"),
            "Sec-Fetch-Site": request.headers.get("Sec-Fetch-Site", "cross-site"),
            "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }
        if upstream_referer:
            proxy_headers["Referer"] = upstream_referer
        if upstream_origin:
            proxy_headers["Origin"] = upstream_origin
        if "Range" in request.headers:
            proxy_headers["Range"] = request.headers["Range"]
        if "If-Range" in request.headers:
            proxy_headers["If-Range"] = request.headers["If-Range"]
        r = requests.get(target, headers=proxy_headers, stream=True, timeout=(5, 15), allow_redirects=True)
        content_encoding = r.headers.get('Content-Encoding', '').lower()
        if content_encoding == 'br' and brotli is not None:
            r._content = brotli.decompress(r.content)
            r.headers.pop('Content-Encoding', None)
        elif content_encoding in {'gzip', 'deflate'}:
            r.headers.pop('Content-Encoding', None)
        excluded = {'content-encoding','content-length','transfer-encoding','connection','content-type','x-frame-options','content-security-policy','content-security-policy-report-only','x-content-type-options','x-xss-protection'}
        resp_headers = {}
        for k, v in r.headers.items():
            if k.lower() not in excluded:
                resp_headers[k] = v
        resp_headers['Access-Control-Allow-Origin'] = '*'
        resp_headers['Access-Control-Allow-Headers'] = '*'
        resp_headers['Access-Control-Expose-Headers'] = '*'
        resp_headers['X-Frame-Options'] = 'ALLOWALL'
        resp_headers['Content-Security-Policy'] = "frame-ancestors *"
        content_type = r.headers.get('Content-Type', '').split(';', 1)[0].strip().lower()
        if expected_mime:
            content_type = expected_mime
            resp_headers['Content-Type'] = expected_mime

            # Do not expose an upstream HTML error page as a JavaScript/CSS asset.
            if r.status_code >= 400:
                r.close()
                return Response('', status=200, headers={**resp_headers, 'X-Proxy-Fallback': 'asset-error'})

        if not content_type:
            guessed_type, _ = mimetypes.guess_type(target_path)
            content_type = guessed_type or 'application/octet-stream'
            resp_headers['Content-Type'] = content_type
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
        fallback_mime = locals().get('expected_mime')
        if fallback_mime:
            return Response('', status=200, headers={
                'Content-Type': fallback_mime,
                'X-Proxy-Fallback': 'asset-request-error',
                'Access-Control-Allow-Origin': '*',
            })
        return f"Proxy error: {e}", 502

@app.route('/proxy-stream')
def proxy_stream():
    target_url = request.args.get('url')
    if not target_url:
        return "URL tidak valid", 400
    # Handle nested proxy from anichin-player
    if "anichin-player.web.id/api/proxy-player" in target_url:
        nested_url = parse_qs(urlparse(target_url).query).get('url', [''])[0]
        if nested_url:
            target_url = unquote(nested_url)
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
@limiter.limit("5 per minute")
def api_register():
    if not validate_csrf_token():
        return jsonify({"status":"error","message":"CSRF token tidak valid"}), 403
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

    if USE_SUPABASE:
        try:
            existing = supabase.table("users").select("id").or_(f"username.eq.{username},email.eq.{email}").execute()
            if existing.data:
                return jsonify({"status":"error","message":"Username atau email sudah dipakai"}), 400
            hashed_pw = generate_password_hash(password)
            res = supabase.table("users").insert({"username": username, "email": email, "password_hash": hashed_pw, "email_verified": False}).execute()
            uid = res.data[0]["id"]
        except Exception as e:
            return jsonify({"status":"error","message":f"Registrasi gagal: {str(e)}"}), 500
    else:
        conn = get_db()
        if conn.execute('SELECT id FROM users WHERE username=?', (username,)).fetchone():
            conn.close(); return jsonify({"status":"error","message":"Username sudah dipakai"}), 400
        if conn.execute('SELECT id FROM users WHERE email=?', (email,)).fetchone():
            conn.close(); return jsonify({"status":"error","message":"Email sudah terdaftar"}), 400
        hashed_pw = generate_password_hash(password)
        cur = conn.execute('INSERT INTO users (username,email,password_hash,email_verified) VALUES (?,?,?,0)', (username,email,hashed_pw))
        conn.commit()
        uid = cur.lastrowid
        conn.close()

    # Generate verification token
    token = secrets.token_urlsafe(32)
    email_verify_tokens[token] = {"user_id": uid, "email": email, "expires": time.time() + 86400}  # 24 hours

    # Send verification email
    send_verification_email(email, username, token)

    add_dev_log(f"User registered (unverified): {username}", 'INFO', 'auth')
    return jsonify({"status":"success","message":"Registrasi berhasil! Silakan cek email kamu untuk verifikasi.","need_verify":True,"email":email})

@app.route('/verify-email-sent')
def verify_email_sent():
    email = request.args.get('email', '')
    return render_template('verify-email-sent.html', email=email)

@app.route('/verify-email')
def verify_email_page():
    token = request.args.get('token', '').strip()
    if not token:
        return render_template('verify-email.html', status='invalid', message='Token tidak valid')
    info = email_verify_tokens.get(token)
    if not info:
        return render_template('verify-email.html', status='invalid', message='Token tidak ditemukan atau sudah expired')
    if time.time() > info['expires']:
        del email_verify_tokens[token]
        return render_template('verify-email.html', status='expired', message='Token sudah expired, silakan daftar ulang')
    # Mark user as verified
    user_id = info['user_id']
    if USE_SUPABASE:
        try:
            supabase.table("users").update({"email_verified": True}).eq("id", user_id).execute()
        except Exception as e:
            return render_template('verify-email.html', status='error', message=f'Gagal verifikasi: {str(e)}')
    else:
        conn = get_db()
        conn.execute('UPDATE users SET email_verified=1 WHERE id=?', (user_id,))
        conn.commit()
        conn.close()
    del email_verify_tokens[token]
    add_dev_log(f"Email verified: user_id={user_id}", 'INFO', 'auth')
    return render_template('verify-email.html', status='success', message='Email berhasil diverifikasi! Kamu bisa login sekarang.')

@app.route('/api/auth/resend-verification', methods=['POST'])
@limiter.limit("3 per minute")
def api_resend_verification():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    if not email:
        return jsonify({"status":"error","message":"Email wajib diisi"}), 400
    # Find user
    if USE_SUPABASE:
        try:
            res = supabase.table("users").select("id,username,email,email_verified").eq("email", email).execute()
            user = res.data[0] if res.data else None
        except:
            user = None
    else:
        conn = get_db()
        row = conn.execute('SELECT id,username,email,email_verified FROM users WHERE email=?', (email,)).fetchone()
        user = dict(row) if row else None
        conn.close()
    if not user:
        return jsonify({"status":"error","message":"Email tidak terdaftar"}), 404
    if user.get('email_verified'):
        return jsonify({"status":"success","message":"Email sudah terverifikasi, silakan login"})
    # Remove old tokens for this email
    tokens_to_remove = [t for t, v in email_verify_tokens.items() if v['email'] == email]
    for t in tokens_to_remove:
        del email_verify_tokens[t]
    # Generate new token
    token = secrets.token_urlsafe(32)
    email_verify_tokens[token] = {"user_id": user['id'], "email": email, "expires": time.time() + 86400}
    send_verification_email(email, user['username'], token)
    return jsonify({"status":"success","message":"Email verifikasi baru sudah dikirim!"})

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def api_login():
    if not validate_csrf_token():
        return jsonify({"status":"error","message":"CSRF token tidak valid"}), 403
    data = request.get_json() or request.form
    ident = (data.get('username') or data.get('email') or '').strip()
    password = data.get('password') or ''
    if not ident or not password:
        return jsonify({"status":"error","message":"Username/email & password wajib"}),400

    if USE_SUPABASE:
        try:
            res = supabase.table("users").select("*").or_(f"username.eq.{ident.lower()},email.eq.{ident.lower()},username.eq.{ident},email.eq.{ident}").execute()
            row = res.data[0] if res.data else None
        except Exception as e:
            return jsonify({"status":"error","message":f"Login gagal: {str(e)}"}), 500
    else:
        conn = get_db()
        row = conn.execute('SELECT * FROM users WHERE username=? OR email=?', (ident.lower(), ident.lower())).fetchone()
        if not row:
            row = conn.execute('SELECT * FROM users WHERE username=? OR email=?', (ident, ident)).fetchone()
        conn.close()
        row = dict(row) if row else None

    if not row or not row.get('password_hash'):
        return jsonify({"status":"error","message":"Kredensial salah"}),401

    stored_hash = row['password_hash']
    password_match = False

    if stored_hash.startswith('pbkdf2:') or stored_hash.startswith('scrypt:'):
        password_match = check_password_hash(stored_hash, password)
    else:
        password_match = (stored_hash == password)
        if password_match:
            new_hash = generate_password_hash(password)
            if USE_SUPABASE:
                try:
                    supabase.table("users").update({"password_hash": new_hash}).eq("id", row['id']).execute()
                except:
                    pass
            else:
                try:
                    conn2 = get_db()
                    conn2.execute('UPDATE users SET password_hash=? WHERE id=?', (new_hash, row['id']))
                    conn2.commit()
                    conn2.close()
                except:
                    pass

    if not password_match:
        return jsonify({"status":"error","message":"Kredensial salah"}),401
    # Check email verification
    is_verified = row.get('email_verified')
    if not is_verified and row.get('email'):
        return jsonify({"status":"error","message":"Email belum diverifikasi. Silakan cek inbox kamu.","not_verified":True,"email":row.get('email')}),403
    remember = data.get('remember', True)
    session.permanent = bool(remember)
    session['user_id']=row['id']
    session['username']=row['username']
    session['is_admin'] = str(row['username'] or '').lower() in DEV_PANEL_ADMINS
    add_dev_log(f"User login: {row['username']}", 'INFO', 'auth')
    return jsonify({"status":"success","message":"Login berhasil","user":{"id":row['id'],"username":row['username'],"email":row.get('email'),"avatar":row.get('avatar')}})

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

    if USE_SUPABASE:
        try:
            existing = supabase.table("users").select("*").eq("email", email).limit(1).execute()
            row = existing.data[0] if existing.data else None
            if row:
                if not row.get('google_id') and google_id:
                    supabase.table("users").update({"google_id": google_id, "avatar": picture or row.get('avatar')}).eq("id", row["id"]).execute()
                uid = row["id"]
                username = row["username"]
            else:
                username = base_username
                i = 1
                while True:
                    check = supabase.table("users").select("id").eq("username", username).limit(1).execute()
                    if not check.data:
                        break
                    username = f"{base_username}{i}"
                    i += 1
                res = supabase.table("users").insert({"username": username, "email": email, "google_id": google_id, "avatar": picture}).execute()
                uid = res.data[0]["id"]
        except Exception as e:
            return jsonify({"status": "error", "message": f"Google login gagal: {e}"}), 500
    else:
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

    session.permanent = True
    session['user_id'] = uid
    session['username'] = username
    session['is_admin'] = username.lower() in DEV_PANEL_ADMINS
    add_dev_log(f"Google login: {username}", 'INFO', 'auth')
    return jsonify({"status": "success", "message": "Login Google berhasil", "user": {"id": uid, "username": username, "email": email, "avatar": picture}})

@app.route('/api/auth/me')
def api_me():
    user = get_current_user()
    if not user: return jsonify({"logged_in":False})
    return jsonify({"logged_in":True,"user":{"id":user.get('id'),"username":user.get('username'),"email":user.get('email'),"avatar":user.get('avatar')}})

@app.route('/api/auth/logout', methods=['POST','GET'])
def api_logout():
    username = session.get('username')
    session.clear()
    add_dev_log(f"User logout: {username or 'unknown'}", 'INFO', 'auth')
    return jsonify({"status":"success","message":"Logout berhasil"})


# ---------- Dev Panel ----------
@app.route('/dev-login', methods=['GET', 'POST'])
def dev_login_page():
    if session.get('is_admin'):
        return redirect(url_for('dev_panel_page'))

    if request.method == 'POST':
        secret_key = (request.form.get('secret_key') or request.form.get('passcode') or '').strip()
        if secret_key == DEV_SECRET_KEY:
            session.permanent = True
            session['is_admin'] = True
            session['username'] = 'developer'
            session['user_id'] = 999999
            add_dev_log('Secret admin access granted', 'WARNING', 'security')
            return redirect(url_for('dev_panel_page'))
        return render_template_string('''
            <!doctype html>
            <html lang="id">
            <head>
              <meta charset="UTF-8" />
              <meta name="viewport" content="width=device-width, initial-scale=1.0" />
              <title>Vexora | Secret Login</title>
              <style>
                body{margin:0;display:grid;place-items:center;min-height:100vh;background:radial-gradient(circle at top,#1a1a1a,#050505);font-family:Arial,sans-serif;color:#fff}
                .box{width:min(90vw,420px);background:#111;padding:28px;border:1px solid rgba(255,255,255,0.08);border-radius:18px;box-shadow:0 20px 60px rgba(229,9,20,0.15)}
                h1{margin:0 0 10px;font-size:24px;letter-spacing:1px}
                p{margin:0 0 18px;color:#b2b2b2}
                input{width:100%;box-sizing:border-box;padding:12px 14px;border-radius:10px;border:1px solid rgba(255,255,255,0.12);background:#0a0a0a;color:#fff;margin-bottom:12px}
                button{width:100%;padding:12px;border:none;border-radius:10px;background:#e50914;color:#fff;font-weight:700;cursor:pointer}
                .error{color:#ff8a8a;margin-bottom:12px;font-size:14px}
              </style>
            </head>
            <body>
              <div class="box">
                <h1>VEXORA DEV</h1>
                <p>Secret access required.</p>
                <div class="error">Passcode tidak valid.</div>
                <form method="post">
                  <input type="password" name="secret_key" placeholder="Masukkan secret key" required>
                  <button type="submit">Unlock Dev Panel</button>
                </form>
              </div>
            </body>
            </html>
        ''')

    return render_template_string('''
        <!doctype html>
        <html lang="id">
        <head>
          <meta charset="UTF-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <title>Vexora | Secret Login</title>
          <style>
            body{margin:0;display:grid;place-items:center;min-height:100vh;background:radial-gradient(circle at top,#1a1a1a,#050505);font-family:Arial,sans-serif;color:#fff}
            .box{width:min(90vw,420px);background:#111;padding:28px;border:1px solid rgba(255,255,255,0.08);border-radius:18px;box-shadow:0 20px 60px rgba(229,9,20,0.15)}
            h1{margin:0 0 10px;font-size:24px;letter-spacing:1px}
            p{margin:0 0 18px;color:#b2b2b2}
            input{width:100%;box-sizing:border-box;padding:12px 14px;border-radius:10px;border:1px solid rgba(255,255,255,0.12);background:#0a0a0a;color:#fff;margin-bottom:12px}
            button{width:100%;padding:12px;border:none;border-radius:10px;background:#e50914;color:#fff;font-weight:700;cursor:pointer}
          </style>
        </head>
        <body>
          <div class="box">
            <h1>VEXORA DEV</h1>
            <p>Masukkan passcode untuk membuka panel developer.</p>
            <form method="post">
              <input type="password" name="secret_key" placeholder="Masukkan secret key" required>
              <button type="submit">Unlock Dev Panel</button>
            </form>
          </div>
        </body>
        </html>
    ''')


@app.route('/dev-panel')
@dev_panel_required
def dev_panel_page():
    user = get_current_user()
    return render_template('dev_panel.html', user=user)


@app.route('/api/dev/login', methods=['POST'])
def api_dev_login():
    data = request.get_json(silent=True) or request.form or {}
    secret_key = (data.get('secret_key') or data.get('passcode') or '').strip()
    if secret_key == DEV_SECRET_KEY:
        session.permanent = True
        session['is_admin'] = True
        session['username'] = 'developer'
        session['user_id'] = 999999
        add_dev_log('Secret admin access granted via API', 'WARNING', 'security')
        return jsonify({"status": "success", "redirect": url_for('dev_panel_page')})
    return jsonify({"status": "error", "message": "Passcode salah"}), 401


@app.route('/api/dev/logout', methods=['POST'])
def api_dev_logout():
    username = session.get('username')
    session.clear()
    add_dev_log(f"Secret admin logout: {username or 'unknown'}", 'INFO', 'security')
    return jsonify({"status": "success", "message": "Admin session closed"})


@app.route('/dev-logout')
def dev_logout_page():
    session.clear()
    return redirect(url_for('index'))


@app.route('/api/dev/stats')
@dev_panel_required
def api_dev_stats():
    table_counts = {'users': 0, 'bookmarks': 0, 'history': 0, 'cache': 0, 'dev_logs': 0}
    if USE_SUPABASE:
        for table_name in table_counts:
            primary_column = 'key' if table_name == 'cache' else 'id'
            try:
                table_counts[table_name] = len(supabase.table(table_name).select(primary_column).execute().data or [])
            except Exception as exc:
                if table_name == 'users':
                    add_dev_log(f'Dev stats user count failed: {exc}', 'ERROR', 'database')
        total_users = table_counts['users']
    else:
        conn = get_db()
        total_users = conn.execute('SELECT COUNT(*) AS total FROM users').fetchone()['total']
        for table_name in ('bookmarks', 'history', 'cache', 'dev_logs'):
            table_exists = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table_name,)).fetchone()
            if table_exists:
                table_counts[table_name] = conn.execute(f'SELECT COUNT(*) AS total FROM {table_name}').fetchone()['total']
        table_counts['users'] = total_users
        conn.close()

    cache_entries = len(_manual_cache)
    cache_status = 'enabled' if cache is not None else 'manual-fallback'
    db_size_bytes = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
    db_backend = 'supabase' if USE_SUPABASE else 'sqlite'
    if USE_SUPABASE:
        db_size_bytes = 0
        try:
            cache_entries = table_counts['cache']
            cache_status = 'supabase'
        except Exception as exc:
            add_dev_log(f'Dev stats cache count failed: {exc}', 'ERROR', 'database')
            cache_status = 'supabase-error'
    try:
        latest_logs = read_dev_logs(1)
        latest_log = latest_logs[-1] if latest_logs else None
    except Exception as exc:
        add_dev_log(f'Dev stats log read failed: {exc}', 'ERROR', 'database')
        latest_log = _dev_logs[-1] if _dev_logs else None
    if cache is not None and not USE_SUPABASE:
        try:
            cache_entries = getattr(cache, 'cache', {}).__len__() if hasattr(cache, 'cache') else cache_entries
        except Exception:
            pass

    uptime_seconds = int(time.time() - APP_START_TIME)
    upload_storage = get_upload_storage_stats()
    device = get_device_telemetry()
    stats = {
        'total_users': total_users,
        'cache_status': cache_status,
        'cache_entries': cache_entries,
        'uptime_seconds': uptime_seconds,
        'uptime_human': time.strftime('%H:%M:%S', time.gmtime(uptime_seconds)),
        'db_path': DB_PATH if not USE_SUPABASE else 'Supabase project',
        'db_backend': db_backend,
        'db_size_bytes': db_size_bytes,
        'server_status': 'online',
        'admin_user': session.get('username'),
        'latest_log': latest_log,
        'storage': {
            'provider': 'Supabase PostgreSQL' if USE_SUPABASE else 'SQLite',
            'location': 'Cloud project' if USE_SUPABASE else DB_PATH,
            'connection': 'connected' if USE_SUPABASE or os.path.exists(DB_PATH) else 'unavailable',
            'cache_table': 'connected' if cache_status == 'supabase' else cache_status,
            'dev_logs_table': 'connected' if _supabase_dev_logs_available is not False or not USE_SUPABASE else 'setup required',
            'uploads_files': upload_storage['files'],
            'uploads_bytes': upload_storage['bytes'],
            'table_counts': table_counts,
            'cache_ttl_seconds': DB_CACHE_TTL,
        },
        'device': device,
    }
    return jsonify({"status": "success", "stats": stats})


@app.route('/api/dev/clear-cache', methods=['POST'])
@dev_panel_required
def api_clear_cache():
    _manual_cache.clear()
    if USE_SUPABASE:
        supabase.table('cache').delete().neq('key', '').execute()
    else:
        ensure_cache_table()
        db_conn = get_db()
        db_conn.execute('DELETE FROM cache')
        db_conn.commit()
        db_conn.close()
    if cache is not None:
        try:
            cache.clear()
        except Exception:
            pass
    add_dev_log(f"Cache cleared by {session.get('username')}", 'WARNING', 'cache')
    return jsonify({"status": "success", "message": "Cache scraper berhasil dibersihkan"})


@app.route('/api/dev/refresh-scraper', methods=['POST'])
@dev_panel_required
def api_refresh_scraper():
    try:
        banner_count = len(scrape_banner_data())
        schedule_count = len(scrape_schedule_data())
        add_dev_log(f"Scraper refresh triggered by {session.get('username')} (banner={banner_count}, schedule={schedule_count})", 'INFO', 'scraper')
        return jsonify({"status": "success", "message": "Scraper berhasil di-refresh", "banner_count": banner_count, "schedule_count": schedule_count})
    except Exception as exc:
        add_dev_log(f"Scraper refresh failed: {exc}", 'ERROR', 'scraper')
        return jsonify({"status": "error", "message": f"Refresh scraper gagal: {exc}"}), 500


@app.route('/api/dev/sync-all', methods=['POST'])
@dev_panel_required
def api_dev_sync_all():
    started = time.time()
    def collect_banner():
        data = scrape_banner_data()
        return 'scraper.banner', {"creator":"Vexalyn Developer","status":"success","total_banners":len(data),"banners":data}
    def collect_schedule():
        data = scrape_schedule_data()
        return 'scraper.schedule', {"creator":"Vexalyn Developer","status":"success","total_days":len(data),"schedule":data}
    def collect_home():
        with app.test_request_context('/api/home'):
            return 'scraper.home', api_home().get_json()
    def collect_genres():
        with app.test_request_context('/api/genres'):
            return 'scraper.genres', api_all_genres().get_json()

    results = {}
    failures = {}
    payloads = {}
    with ThreadPoolExecutor(max_workers=4, thread_name_prefix='sync-scraper') as executor:
        futures = [executor.submit(loader) for loader in (collect_home, collect_banner, collect_schedule, collect_genres)]
        for future in as_completed(futures):
            try:
                key, payload = future.result()
                write_db_cache(key, payload)
                results[key] = 'updated'
                payloads[key] = payload
            except Exception as exc:
                failures[str(exc)] = 'failed'
    add_dev_log(f"Full scraper sync by {session.get('username')} ({len(results)} updated)", 'INFO', 'scraper')
    return jsonify({'status': 'success' if not failures else 'partial', 'duration_seconds': round(time.time() - started, 2), 'updated': results, 'payloads': payloads, 'failures': failures})


@app.route('/api/dev/terminal', methods=['GET', 'POST'])
@dev_panel_required
def api_dev_terminal():
    commands = {
        'system.status': 'Live server, cache, uptime, and database snapshot',
        'system.health': 'Check the active service health state',
        'system.version': 'Show the Vexora operations runtime version',
        'system.logs': 'Show the latest runtime transmissions',
        'users.count': 'Count users in the active database',
        'scraper.banner': 'Read the current featured banner data',
        'sync_all': 'Run every registered scraper and update database cache',
        'cache.clear': 'Clear the application cache',
        'scraper.refresh': 'Refresh banner and schedule data',
    }
    if request.method == 'GET':
        stats = api_dev_stats().get_json()['stats']
        device = stats['device']
        gib = lambda value: f"{value / (1024 ** 3):.2f} GiB"
        globe = [
            '⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⣤⣤⣤⡼⠀⢀⡀⣀⢱⡄⡀⠀⠀⠀⢲⣤⣤⣤⣤⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀',
            '⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣾⣿⣿⣿⣿⣿⡿⠛⠋⠁⣤⣿⣿⣿⣧⣷⠀⠀⠘⠉⠛⢻⣷⣿⣽⣿⣿⣷⣦⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀',
            '⠀⠀⠀⠀⠀⠀⢀⣴⣞⣽⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠠⣿⣿⡟⢻⣿⣿⣇⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣟⢦⡀⠀⠀⠀⠀⠀⠀',
            '⠀⠀⠀⠀⠀⣠⣿⡾⣿⣿⣿⣿⣿⠿⣻⣿⣿⡀⠀⠀⠀⢻⣿⣷⡀⠻⣧⣿⠆⠀⠀⠀⠀⣿⣿⣿⡻⣿⣿⣿⣿⣿⠿⣽⣦⡀⠀⠀⠀⠀',
            '⠀⠀⠀⠀⣼⠟⣩⾾⣿⣿⣿⢟⣵⣾⣿⣿⣿⣧⠀⠀⠀⠈⠿⣿⣿⣷⣈⠁⠀⠀⠀⠀⣰⣿⣿⣿⣿⣮⣟⢯⣿⣿⣷⣬⡻⣷⡄⠀⠀⠀',
            '⠀⠀⢀⡜⣡⣾⣿⢿⣿⣿⣿⣿⣿⢟⣵⣿⣿⣿⣷⣄⠀⣰⣿⣿⣿⣿⣿⣷⣄⠀⢀⣼⣿⣿⣿⣷⡹⣿⣿⣿⣿⣿⣿⢿⣿⣮⡳⡄⠀⠀',
            '⠀⢠⢟⣿⡿⠋⣠⣾⢿⣿⣿⠟⢃⣾⢟⣿⢿⣿⣿⣿⣾⡿⠟⠻⣿⣻⣿⣏⠻⣿⣾⣿⣿⣿⣿⡛⣿⡌⠻⣿⣿⡿⣿⣦⡙⢿⣿⡝⣆⠀',
            '⠀⢯⣿⠏⣠⠞⠋⠀⣠⡿⠋⢀⣿⠁⢸⡏⣿⠿⣿⣿⠃⢠⣴⣾⣿⣿⣿⡟⠀⠘⢹⣿⠟⣿⣾⣷⠈⣿⡄⠘⢿⣦⠀⠈⠻⣆⠙⣿⣜⠆',
            '⢀⣿⠃⡴⠃⢀⡠⠞⠋⠀⠀⠼⠋⠀⠸⡇⠻⠀⠈⠃⠀⣧⢋⣼⣿⣿⣿⣷⣆⠀⠈⠁⠀⠟⠁⡟⠀⠈⠻⠀⠀⠉⠳⢦⡀⠈⢣⠈⢿⡄',
            '⣸⠇⢠⣷⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⠿⠿⠋⠀⢻⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢾⣆⠈⣷',
            '⡟⠀⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣶⣤⡀⢸⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡄⢹',
            '⡇⠀⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠈⣿⣼⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠃⢸',
            '⢡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⠶⣶⡟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼',
            '⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁',
            '⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀',
        ]
        info = [
            '<span class="boot-name">nova@vexora</span>',
            '<span class="boot-cyan">▣</span> <b> NOVA OS // VEXORA SHELL</b>',
            f'<span class="boot-pink">⚙</span> <b> {html.escape(device["os"])} ({html.escape(device["architecture"])})</b>',
            f'<span class="boot-orange">▣</span> <b> {html.escape(device["cpu"])} ({device["cpu_count"]} threads)</b>',
            f'<span class="boot-green">▤</span> <b> {gib(device["memory_used"])} / {gib(device["memory_total"])} ({device["memory_percent"]}%)</b>',
            '<span class="boot-dots"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></span>',
        ]
        boot_markup = (
            '<div class="boot-layout">'
            '<div class="boot-art">'
            + html.escape('\n'.join(globe))
            + '</div><div class="boot-info">'
            + '<br>'.join(info)
            + '</div></div>'
        )
        boot_markup += '\n'.join([
            '',
            '<span class="boot-dim">SECURE UPLINK ESTABLISHED // {0} COMMANDS LOADED</span>'.format(len(commands)),
            '<span class="boot-prompt">nova@vexora ~ $</span>',
        ])
        return jsonify({'status': 'success', 'commands': commands, 'boot': boot_markup})

    command = (request.get_json(silent=True) or {}).get('command', '').strip().lower()
    if command not in commands:
        return jsonify({'status': 'error', 'message': 'Command not registered', 'commands': commands}), 400

    if command == 'system.status' or command == 'system.health':
        stats_response = api_dev_stats()
        stats = stats_response.get_json()['stats']
        if command == 'system.health':
            output = '\n'.join([
                'SERVICE HEALTH',
                f"[OK] SERVER     {stats['server_status']}",
                f"[OK] DATABASE   {'connected' if USE_SUPABASE or os.path.exists(DB_PATH) else 'unavailable'}",
                f"[OK] CACHE      {stats['cache_status']}",
                f"[OK] SCRAPER    ready",
            ])
        else:
            output = '\n'.join([
            f"SERVER   {stats['server_status']}",
            f"USERS    {stats['total_users']}",
            f"CACHE    {stats['cache_status']} ({stats['cache_entries']} entries)",
            f"UPTIME   {stats['uptime_human']}",
            f"DB SIZE  {stats['db_size_bytes']} bytes",
            ])
    elif command == 'system.version':
        output = 'VEXORA OPERATIONS RUNTIME\nNOVA OS v1.0\nFIELD TERMINAL PROTOCOL 1.0'
    elif command == 'system.logs':
        output = '\n'.join(f"[{log['timestamp']}] {log['level']:<7} {log['category']}: {log['message']}" for log in _dev_logs[-12:]) or 'No transmissions recorded.'
    elif command == 'users.count':
        stats_response = api_dev_stats()
        output = f"ACTIVE DATABASE USERS: {stats_response.get_json()['stats']['total_users']}"
    elif command == 'sync_all':
        sync_response = api_dev_sync_all()
        sync_data = sync_response.get_json()
        output_lines = [
            'VEXORA SCRAPER SYNC',
            f"DURATION  {sync_data.get('duration_seconds', 0)} seconds",
        ]
        payloads = sync_data.get('payloads', {})
        home = payloads.get('scraper.home', {})
        banner = payloads.get('scraper.banner', {})
        schedule = payloads.get('scraper.schedule', {})
        genres = payloads.get('scraper.genres', {})
        details = {
            'scraper.home': f"{len(home.get('sections', []))} sections / {sum(len(section.get('data', [])) for section in home.get('sections', []))} titles",
            'scraper.banner': f"{banner.get('total_banners', len(banner.get('banners', [])))} banners",
            'scraper.schedule': f"{schedule.get('total_days', len(schedule.get('schedule', [])))} release days",
            'scraper.genres': f"{genres.get('total', genres.get('total_genres', len(genres.get('data', []))))} genres",
        }
        for key, detail in details.items():
            output_lines.append(f"[OK]      {key:<17} {detail}" if key in sync_data.get('updated', {}) else f"[FAILED]  {key}")
        if sync_data.get('failures'):
            output_lines.extend(f"ERROR     {message}" for message in sync_data['failures'])
        output = '\n'.join(output_lines)
    elif command == 'scraper.banner':
        banners = scrape_banner_data()
        if banners:
            featured = banners[0]
            output = '\n'.join([
                'FEATURED BANNER',
                f"TITLE    {featured.get('title', 'Unknown')}",
                f"SYNOPSIS {featured.get('synopsis', 'Unavailable')}",
                f"IMAGE    {featured.get('thumbnail', 'Unavailable')}",
                f"TOTAL    {len(banners)} banners available",
            ])
        else:
            output = 'FEATURED BANNER\nNo banner data available.'
    elif command == 'cache.clear':
        _manual_cache.clear()
        if cache is not None:
            cache.clear()
        add_dev_log(f"Terminal cache clear by {session.get('username')}", 'WARNING', 'cache')
        output = 'CACHE VAULT CLEARED.'
    else:
        try:
            banner_count = len(scrape_banner_data())
            schedule_count = len(scrape_schedule_data())
            add_dev_log(f"Terminal scraper refresh by {session.get('username')} (banner={banner_count}, schedule={schedule_count})", 'INFO', 'scraper')
            output = f"SCRAPER REFRESHED.\nBANNERS  {banner_count}\nSCHEDULE {schedule_count}"
        except Exception as exc:
            add_dev_log(f'Terminal scraper refresh failed: {exc}', 'ERROR', 'scraper')
            return jsonify({'status': 'error', 'message': str(exc)}), 500

    return jsonify({'status': 'success', 'command': command, 'output': output})


@app.route('/api/dev/logs')
@dev_panel_required
def api_dev_logs():
    limit = request.args.get('limit', default=100, type=int)
    limit = max(1, min(limit, 200))
    try:
        logs = read_dev_logs(limit)
    except Exception as exc:
        add_dev_log(f'Dev log query failed: {exc}', 'ERROR', 'database')
        logs = _dev_logs[-limit:]
    return jsonify({"status": "success", "logs": logs, "total": len(logs)})


@app.route('/api/dev/logs/clear', methods=['POST'])
@dev_panel_required
def api_clear_dev_logs():
    _dev_logs.clear()
    try:
        if USE_SUPABASE:
            supabase.table('dev_logs').delete().neq('id', 0).execute()
        else:
            ensure_dev_logs_table()
            conn = get_db()
            conn.execute('DELETE FROM dev_logs')
            conn.commit()
            conn.close()
        return jsonify({"status": "success", "message": "Dev log berhasil dibersihkan"})
    except Exception as exc:
        print(f"[DEV LOG CLEAR ERROR] {exc}")
        return jsonify({"status": "error", "message": "Dev log gagal dibersihkan"}), 500


@app.route('/api/dev/users', methods=['GET'])
@dev_panel_required
def api_dev_users():
    q = (request.args.get('q') or '').strip()
    if USE_SUPABASE:
        try:
            query = supabase.table('users').select('*').order('id', desc=True).limit(200)
            if q:
                query = query.or_(f'username.ilike.%{q}%,email.ilike.%{q}%')
            users = query.execute().data or []
            return jsonify({"status": "success", "total": len(users), "users": users})
        except Exception as exc:
            add_dev_log(f'Dev user listing failed: {exc}', 'ERROR', 'database')
            return jsonify({"status": "error", "message": "User records unavailable"}), 500
    conn = get_db()
    if q:
        rows = conn.execute(
            "SELECT * FROM users WHERE username LIKE ? OR email LIKE ? ORDER BY id DESC LIMIT 100",
            (f'%{q}%', f'%{q}%')
        ).fetchall()
    else:
        rows = conn.execute('SELECT * FROM users ORDER BY id DESC LIMIT 200').fetchall()
    conn.close()
    users = [dict(row) for row in rows]
    return jsonify({"status": "success", "total": len(users), "users": users})


@app.route('/api/dev/users/<int:user_id>', methods=['DELETE'])
@dev_panel_required
def api_dev_delete_user(user_id):
    if user_id == session.get('user_id'):
        return jsonify({"status": "error", "message": "Tidak bisa menghapus akun sendiri dari dev panel"}), 400
    if USE_SUPABASE:
        try:
            result = supabase.table('users').select('username').eq('id', user_id).limit(1).execute()
            if not result.data:
                return jsonify({"status": "error", "message": "User tidak ditemukan"}), 404
            username = result.data[0].get('username') or str(user_id)
            supabase.table('users').delete().eq('id', user_id).execute()
            add_dev_log(f"User deleted by {session.get('username')}: {username}", 'WARNING', 'users')
            return jsonify({"status": "success", "message": f"User {username} berhasil dihapus"})
        except Exception as exc:
            add_dev_log(f'Dev user deletion failed: {exc}', 'ERROR', 'database')
            return jsonify({"status": "error", "message": "User deletion failed"}), 500
    conn = get_db()
    row = conn.execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"status": "error", "message": "User tidak ditemukan"}), 404
    conn.execute('DELETE FROM users WHERE id=?', (user_id,))
    conn.commit()
    conn.close()
    add_dev_log(f"User deleted by {session.get('username')}: {row['username']}", 'WARNING', 'users')
    return jsonify({"status": "success", "message": f"User {row['username']} berhasil dihapus"})

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

def send_email_otp(email, otp):
    """Send OTP via Resend Email API with branded VEXORA template"""
    if not RESEND_API_KEY or not HAS_RESEND:
        print(f"[EMAIL OTP] {email} -> {otp} (Resend not available, console only)")
        return False

    LOGO_URL = "https://i.imgur.com/xGSfveu.png"  # Primary: Imgur | Fallbacks: iili.io/Cb5sosn.png, files.catbox.moe/l03o9g.png

    html_body = f'''<!DOCTYPE html>
<html lang="id">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0a;padding:48px 20px">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%">

  <!-- Logo -->
  <tr><td style="padding:0 0 40px">
    <img src="{LOGO_URL}" alt="VEXORA" height="40" style="display:block;height:40px;width:auto">
  </td></tr>

  <!-- Card -->
  <tr><td style="background:#141414;border-radius:14px;overflow:hidden;border:1px solid rgba(255,255,255,0.06)">

    <!-- Red Accent Bar -->
    <div style="height:3px;background:linear-gradient(90deg,#e50914 0%,#ff3b44 50%,#e50914 100%)"></div>

    <!-- Content -->
    <div style="padding:48px">

      <!-- Title -->
      <h1 style="color:#ffffff;font-size:24px;font-weight:800;margin:0 0 8px;letter-spacing:-0.3px">Verifikasi Email</h1>
      <p style="color:#b3b3b3;font-size:14px;line-height:1.6;margin:0 0 40px">Masukkan kode verifikasi di bawah ini untuk menyelesaikan proses autentikasi akun VEXORA Anda.</p>

      <!-- OTP Digits -->
      <table cellpadding="0" cellspacing="10" style="margin:0 0 24px">
        <tr>
          {"".join(f'<td style="background:#e50914;width:56px;height:66px;border-radius:10px;text-align:center;vertical-align:middle;box-shadow:0 0 20px rgba(229,9,20,0.3)"><span style="color:#ffffff;font-size:28px;font-weight:800;font-family:Georgia,serif">{d}</span></td>' for d in otp)}
        </tr>
      </table>
      <p style="color:#808080;font-size:12px;margin:0 0 40px;letter-spacing:0.5px">KODE BERLAKU SELAMA 5 MENIT &bull; JANGAN BAGIKAN KE SIAPA PUN</p>

      <!-- Divider -->
      <div style="border-top:1px solid rgba(255,255,255,0.06);margin:0 0 32px"></div>

      <!-- Warning -->
      <table cellpadding="0" cellspacing="0" width="100%">
        <tr>
          <td style="width:24px;vertical-align:top;padding-top:2px">
            <div style="width:20px;height:20px;background:rgba(229,9,20,0.15);border-radius:50%;text-align:center;line-height:20px">
              <span style="color:#e50914;font-size:11px;font-weight:800">!</span>
            </div>
          </td>
          <td style="color:#b3b3b3;font-size:13px;line-height:1.6;padding-left:12px">
            Jika Anda tidak merasa melakukan permintaan ini, cukup abaikan email ini. Keamanan akun Anda tetap terjaga.
          </td>
        </tr>
      </table>

    </div>

  </td></tr>

  <!-- Footer -->
  <tr><td style="padding:32px 0 0">
    <table cellpadding="0" cellspacing="0" width="100%">
      <tr>
        <td style="color:#525252;font-size:11px;letter-spacing:0.5px">&copy; 2026 VEXORA. All rights reserved.</td>
        <td style="color:#525252;font-size:11px;text-align:right;letter-spacing:0.5px">Dikembangkan oleh <span style="color:#e50914;font-weight:700">Vexalyn Developer</span></td>
      </tr>
    </table>
  </td></tr>

</table>
</td></tr></table>
</body></html>'''

    try:
        result = resend.Emails.send({
            "from": f"VEXORA <{RESEND_FROM_EMAIL}>",
            "to": [email],
            "subject": f"Kode Verifikasi VEXORA: {otp}",
            "html": html_body
        })
        print(f"[EMAIL OTP] {email} -> sent, id={result.get('id','?')}")
        return True
    except Exception as e:
        error_text = str(e)
        if "401" in error_text or "api key" in error_text.lower() or "unauthorized" in error_text.lower():
            print("[EMAIL ERROR] Resend rejected the API key (401 Unauthorized)")
        else:
            print(f"[EMAIL ERROR] {error_text}")
        return False

def send_verification_email(email, username, token):
    """Send email verification link via Resend"""
    if not RESEND_API_KEY or not HAS_RESEND:
        print(f"[EMAIL VERIFY] {email} -> token={token} (Resend not available, console only)")
        return False

    LOGO_URL = "https://i.imgur.com/xGSfveu.png"  # Primary: Imgur | Fallbacks: iili.io/Cb5sosn.png, files.catbox.moe/l03o9g.png
    verify_url = f"{request.host_url}verify-email?token={token}"

    html_body = f'''<!DOCTYPE html>
<html lang="id">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0a;padding:48px 20px">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%">

  <tr><td style="padding:0 0 40px">
    <img src="{LOGO_URL}" alt="VEXORA" height="40" style="display:block;height:40px;width:auto">
  </td></tr>

  <tr><td style="background:#141414;border-radius:14px;overflow:hidden;border:1px solid rgba(255,255,255,0.06)">

    <div style="height:3px;background:linear-gradient(90deg,#e50914 0%,#ff3b44 50%,#e50914 100%)"></div>

    <div style="padding:48px">

      <h1 style="color:#ffffff;font-size:24px;font-weight:800;margin:0 0 8px;letter-spacing:-0.3px">Verifikasi Email</h1>
      <p style="color:#b3b3b3;font-size:14px;line-height:1.6;margin:0 0 8px">Halo <strong style="color:#ffffff">{username}</strong>,</p>
      <p style="color:#b3b3b3;font-size:14px;line-height:1.6;margin:0 0 36px">Klik tombol di bawah ini untuk memverifikasi email kamu dan mengaktifkan akun VEXORA.</p>

      <table cellpadding="0" cellspacing="0" style="margin:0 0 32px">
        <tr>
          <td style="background:#e50914;border-radius:4px">
            <a href="{verify_url}" style="display:inline-block;color:#ffffff;font-size:15px;font-weight:700;padding:14px 48px;text-decoration:none">Verifikasi Sekarang</a>
          </td>
        </tr>
      </table>

      <div style="border-top:1px solid rgba(255,255,255,0.06);margin:0 0 28px"></div>

      <p style="color:#808080;font-size:13px;line-height:1.6;margin:0 0 8px">Atau salin link ini ke browser kamu:</p>
      <p style="color:#e50914;font-size:13px;word-break:break-all;margin:0 0 28px">{verify_url}</p>

      <table cellpadding="0" cellspacing="0" width="100%">
        <tr>
          <td style="width:24px;vertical-align:top;padding-top:2px">
            <div style="width:20px;height:20px;background:rgba(229,9,20,0.15);border-radius:50%;text-align:center;line-height:20px">
              <span style="color:#e50914;font-size:11px;font-weight:800">!</span>
            </div>
          </td>
          <td style="color:#b3b3b3;font-size:13px;line-height:1.6;padding-left:12px">
            Link ini berlaku selama <strong style="color:#ffffff">24 jam</strong>. Jika kamu tidak mendaftar, abaikan email ini.
          </td>
        </tr>
      </table>

    </div>

  </td></tr>

  <tr><td style="padding:32px 0 0">
    <table cellpadding="0" cellspacing="0" width="100%">
      <tr>
        <td style="color:#525252;font-size:11px;letter-spacing:0.5px">&copy; 2026 VEXORA. All rights reserved.</td>
        <td style="color:#525252;font-size:11px;text-align:right;letter-spacing:0.5px">Dikembangkan oleh <span style="color:#e50914;font-weight:700">Vexalyn Developer</span></td>
      </tr>
    </table>
  </td></tr>

</table>
</td></tr></table>
</body></html>'''

    try:
        result = resend.Emails.send({
            "from": f"VEXORA <{RESEND_FROM_EMAIL}>",
            "to": [email],
            "subject": "Verifikasi Email Akun VEXORA Kamu",
            "html": html_body
        })
        print(f"[EMAIL VERIFY] {email} -> sent, id={result.get('id','?')}")
        return True
    except Exception as e:
        error_text = str(e)
        if "401" in error_text or "api key" in error_text.lower() or "unauthorized" in error_text.lower():
            print("[EMAIL ERROR] Resend rejected the API key (401 Unauthorized)")
        else:
            print(f"[EMAIL ERROR] {error_text}")
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

    if USE_SUPABASE:
        try:
            existing = supabase.table("users").select("*").eq("phone", phone).limit(1).execute()
            row = existing.data[0] if existing.data else None
            if row:
                uid = row["id"]
                username = row["username"]
            else:
                username = (data.get('username') or '').strip() or f"user_{phone[-4:]}"
                i = 1
                while True:
                    check = supabase.table("users").select("id").eq("username", username).limit(1).execute()
                    if not check.data:
                        break
                    username = f"{username}_{i}"
                    i += 1
                res = supabase.table("users").insert({"username": username, "phone": phone}).execute()
                uid = res.data[0]["id"]
        except Exception as e:
            return jsonify({"status":"error","message":str(e)}), 500
    else:
        conn = get_db()
        row = conn.execute('SELECT * FROM users WHERE phone=?', (phone,)).fetchone()
        if row:
            uid = row['id']
            username = row['username']
        else:
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

# ---------- Forgot Password ----------
@app.route('/api/auth/forgot-password', methods=['POST'])
@limiter.limit("3 per minute")
def forgot_password():
    data = request.get_json(silent=True) or request.form
    email = (data.get('email') or '').strip().lower()
    phone = (data.get('phone') or '').strip()
    phone = re.sub(r'[\s\-\.\(\)]', '', phone)

    if not email and not phone:
        return jsonify({"status": "error", "message": "Email atau nomor telepon wajib diisi"}), 400

    if USE_SUPABASE:
        if email:
            try:
                existing = supabase.table("users").select("id").eq("email", email).limit(1).execute()
                if not existing.data:
                    return jsonify({"status": "error", "message": "Email tidak terdaftar"}), 404
            except Exception as e:
                return jsonify({"status":"error","message":str(e)}), 500
        else:
            try:
                existing = supabase.table("users").select("id").eq("phone", phone).limit(1).execute()
                if not existing.data:
                    return jsonify({"status": "error", "message": "Nomor telepon tidak terdaftar"}), 404
            except Exception as e:
                return jsonify({"status":"error","message":str(e)}), 500
    else:
        conn = get_db()
        if email:
            row = conn.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
            conn.close()
            if not row:
                return jsonify({"status": "error", "message": "Email tidak terdaftar"}), 404
        else:
            row = conn.execute('SELECT * FROM users WHERE phone=?', (phone,)).fetchone()
            conn.close()
            if not row:
                return jsonify({"status": "error", "message": "Nomor telepon tidak terdaftar"}), 404

    if email:
        otp = f"{secrets.randbelow(900000) + 100000}"
        otp_store[f"reset:{email}"] = {"otp": otp, "expires": time.time() + 300}
        sent = send_email_otp(email, otp)
        if sent:
            return jsonify({"status": "success", "message": "Kode verifikasi telah dikirim ke email kamu"})
        if app.debug:
            print(f"[EMAIL DEV FALLBACK] {email} -> {otp}")
            return jsonify({"status": "success", "message": "Mode development: email gagal dikirim, gunakan kode OTP dari terminal.", "otp": otp, "dev_mode": True})
        if RESEND_API_KEY and HAS_RESEND:
            return jsonify({"status": "error", "message": "Email gagal dikirim. API key Resend ditolak atau alamat pengirim belum diverifikasi."}), 502
        resp_data = {"status": "success", "message": "Email belum dikonfigurasi; kode verifikasi tersedia di server."}
        if not RESEND_API_KEY or not HAS_RESEND:
            resp_data["otp"] = otp
        return jsonify(resp_data)
    else:
        otp = f"{secrets.randbelow(900000) + 100000}"
        otp_store[f"reset:{phone}"] = {"otp": otp, "expires": time.time() + 300}
        sent = send_whatsapp_otp(phone, otp)
        if sent:
            return jsonify({"status": "success", "message": "Kode verifikasi telah dikirim ke WhatsApp kamu"})
        resp_data = {"status": "success", "message": f"Kode verifikasi: {otp}"}
        if not FONNTE_TOKEN:
            resp_data["otp"] = otp
        return jsonify(resp_data)

@app.route('/api/auth/verify-reset-otp', methods=['POST'])
@limiter.limit("5 per minute")
def verify_reset_otp():
    data = request.get_json()
    reset_type = data.get('type')
    target = (data.get('target') or '').strip()
    otp_input = (data.get('otp') or '').strip()

    if reset_type == 'email':
        target = target.lower()

    key = f"reset:{target}"
    stored = otp_store.get(key)
    if not stored or stored['otp'] != otp_input:
        return jsonify({"status": "error", "message": "Kode verifikasi salah atau sudah kedaluwarsa"}), 401
    if time.time() > stored['expires']:
        del otp_store[key]
        return jsonify({"status": "error", "message": "Kode verifikasi sudah kedaluwarsa"}), 401

    # OTP valid — store a flag
    otp_store[key]['verified'] = True
    return jsonify({"status": "success", "message": "Kode verifikasi valid"})

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    reset_type = data.get('type')
    target = (data.get('target') or '').strip()
    new_password = data.get('password') or ''

    if reset_type == 'email':
        target = target.lower()

    if len(new_password) < 6:
        return jsonify({"status": "error", "message": "Sandi minimal 6 karakter"}), 400

    key = f"reset:{target}"
    stored = otp_store.get(key)
    if not stored or not stored.get('verified'):
        return jsonify({"status": "error", "message": "Sesi reset tidak valid"}), 401

    del otp_store[key]

    hashed_pw = generate_password_hash(new_password)

    if USE_SUPABASE:
        try:
            if reset_type == 'email':
                supabase.table("users").update({"password_hash": hashed_pw}).eq("email", target).execute()
            else:
                supabase.table("users").update({"password_hash": hashed_pw}).eq("phone", target).execute()
        except Exception as e:
            return jsonify({"status":"error","message":str(e)}), 500
    else:
        conn = get_db()
        if reset_type == 'email':
            conn.execute('UPDATE users SET password_hash=? WHERE email=?', (hashed_pw, target))
        else:
            conn.execute('UPDATE users SET password_hash=? WHERE phone=?', (hashed_pw, target))
        conn.commit()
        conn.close()
    return jsonify({"status": "success", "message": "Sandi berhasil diubah"})

# ---------- Password Reset via Email Token ----------
@app.route('/api/auth/forgot-password-email', methods=['POST'])
@limiter.limit("3 per minute")
def forgot_password_email():
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    if not email:
        return jsonify({"status": "error", "message": "Email wajib diisi"}), 400

    user = None
    if USE_SUPABASE:
        try:
            res = supabase.table("users").select("id,username,email").eq("email", email).limit(1).execute()
            user = res.data[0] if res.data else None
        except Exception as e:
            return jsonify({"status":"error","message":str(e)}), 500
    else:
        conn = get_db()
        row = conn.execute('SELECT id,username,email FROM users WHERE email=?', (email,)).fetchone()
        conn.close()
        user = dict(row) if row else None

    if not user:
        return jsonify({"status": "error", "message": "Email tidak terdaftar"}), 404

    token = secrets.token_urlsafe(32)
    password_reset_tokens[token] = {"user_id": user['id'], "email": email, "expires": time.time() + 3600}

    reset_url = f"{request.host_url}reset-password?token={token}"
    _send_password_reset_email(email, user.get('username', ''), reset_url)

    return jsonify({"status": "success", "message": "Link reset sandi telah dikirim ke email kamu"})

def _send_password_reset_email(email, username, reset_url):
    if not RESEND_API_KEY or not HAS_RESEND:
        print(f"[PASSWORD RESET] {email} -> {reset_url}")
        return False

    LOGO_URL = "https://i.imgur.com/xGSfveu.png"

    html_body = f'''<!DOCTYPE html>
<html lang="id">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0a;padding:48px 20px">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%">

  <tr><td style="padding:0 0 40px">
    <img src="{LOGO_URL}" alt="VEXORA" height="40" style="display:block;height:40px;width:auto">
  </td></tr>

  <tr><td style="background:#141414;border-radius:14px;overflow:hidden;border:1px solid rgba(255,255,255,0.06)">
    <div style="height:3px;background:linear-gradient(90deg,#e50914 0%,#ff3b44 50%,#e50914 100%)"></div>
    <div style="padding:48px">
      <h1 style="color:#ffffff;font-size:24px;font-weight:800;margin:0 0 8px;letter-spacing:-0.3px">Reset Sandi</h1>
      <p style="color:#b3b3b3;font-size:14px;line-height:1.6;margin:0 0 8px">Halo <strong style="color:#ffffff">{username}</strong>,</p>
      <p style="color:#b3b3b3;font-size:14px;line-height:1.6;margin:0 0 36px">Klik tombol di bawah ini untuk membuat sandi baru akun VEXORA kamu.</p>

      <table cellpadding="0" cellspacing="0" style="margin:0 0 32px">
        <tr>
          <td style="background:#e50914;border-radius:4px">
            <a href="{reset_url}" style="display:inline-block;color:#ffffff;font-size:15px;font-weight:700;padding:14px 48px;text-decoration:none">Reset Sandi</a>
          </td>
        </tr>
      </table>

      <div style="border-top:1px solid rgba(255,255,255,0.06);margin:0 0 28px"></div>

      <p style="color:#808080;font-size:13px;line-height:1.6;margin:0 0 8px">Atau salin link ini ke browser kamu:</p>
      <p style="color:#e50914;font-size:13px;word-break:break-all;margin:0 0 28px">{reset_url}</p>

      <table cellpadding="0" cellspacing="0" width="100%">
        <tr>
          <td style="width:24px;vertical-align:top;padding-top:2px">
            <div style="width:20px;height:20px;background:rgba(229,9,20,0.15);border-radius:50%;text-align:center;line-height:20px">
              <span style="color:#e50914;font-size:11px;font-weight:800">!</span>
            </div>
          </td>
          <td style="color:#b3b3b3;font-size:13px;line-height:1.6;padding-left:12px">
            Link ini berlaku selama <strong style="color:#ffffff">1 jam</strong>. Jika kamu tidak meminta reset sandi, abaikan email ini.
          </td>
        </tr>
      </table>
    </div>
  </td></tr>

  <tr><td style="padding:32px 0 0">
    <table cellpadding="0" cellspacing="0" width="100%">
      <tr>
        <td style="color:#525252;font-size:11px;letter-spacing:0.5px">&copy; 2026 VEXORA. All rights reserved.</td>
        <td style="color:#525252;font-size:11px;text-align:right;letter-spacing:0.5px">Dikembangkan oleh <span style="color:#e50914;font-weight:700">Vexalyn Developer</span></td>
      </tr>
    </table>
  </td></tr>

</table>
</td></tr></table>
</body></html>'''

    try:
        result = resend.Emails.send({
            "from": f"VEXORA <{RESEND_FROM_EMAIL}>",
            "to": [email],
            "subject": "Reset Sandi Akun VEXORA",
            "html": html_body
        })
        print(f"[PASSWORD RESET] {email} -> sent, id={result.get('id','?')}")
        return True
    except Exception as e:
        print(f"[PASSWORD RESET] {email} -> error: {e}")
        return False

@app.route('/reset-password')
def reset_password_page():
    token = request.args.get('token', '').strip()
    status = request.args.get('status', '').strip()
    if status == 'success':
        return render_template('reset-password.html', status='success', message='')
    if not token or token not in password_reset_tokens:
        return render_template('reset-password.html', status='invalid', message='Link reset tidak valid')
    info = password_reset_tokens[token]
    if time.time() > info['expires']:
        del password_reset_tokens[token]
        return render_template('reset-password.html', status='expired', message='Link reset sudah expired')
    return render_template('reset-password.html', status='valid', token=token)

@app.route('/api/auth/reset-password-token', methods=['POST'])
@limiter.limit("5 per minute")
def reset_password_token():
    data = request.get_json() or {}
    token = (data.get('token') or '').strip()
    new_password = data.get('password') or ''

    if not token or token not in password_reset_tokens:
        return jsonify({"status": "error", "message": "Token tidak valid"}), 400
    info = password_reset_tokens[token]
    if time.time() > info['expires']:
        del password_reset_tokens[token]
        return jsonify({"status": "error", "message": "Token sudah expired"}), 400
    if len(new_password) < 6:
        return jsonify({"status": "error", "message": "Sandi minimal 6 karakter"}), 400

    del password_reset_tokens[token]
    hashed_pw = generate_password_hash(new_password)
    user_id = info['user_id']

    if USE_SUPABASE:
        try:
            supabase.table("users").update({"password_hash": hashed_pw}).eq("id", user_id).execute()
        except Exception as e:
            return jsonify({"status":"error","message":str(e)}), 500
    else:
        conn = get_db()
        conn.execute('UPDATE users SET password_hash=? WHERE id=?', (hashed_pw, user_id))
        conn.commit()
        conn.close()

    return jsonify({"status": "success", "message": "Sandi berhasil diubah. Silakan masuk."})

@app.route('/api/auth/update-profile', methods=['POST'])
@login_required
def api_update_profile():
    user = get_current_user()
    data = request.get_json() or request.form
    new_username = (data.get('username') or '').strip()
    new_email = (data.get('email') or '').strip().lower()

    if USE_SUPABASE:
        try:
            if new_username and new_username != user['username']:
                check = supabase.table("users").select("id").eq("username", new_username).neq("id", user['id']).limit(1).execute()
                if check.data:
                    return jsonify({"status":"error","message":"Username sudah dipakai"}),400
                supabase.table("users").update({"username": new_username}).eq("id", user['id']).execute()
                session['username'] = new_username
            if new_email and new_email != user.get('email'):
                if not re.match(r'^[^@]+@[^@]+\.[^@]+$', new_email):
                    return jsonify({"status":"error","message":"Email tidak valid"}),400
                check = supabase.table("users").select("id").eq("email", new_email).neq("id", user['id']).limit(1).execute()
                if check.data:
                    return jsonify({"status":"error","message":"Email sudah dipakai"}),400
                supabase.table("users").update({"email": new_email}).eq("id", user['id']).execute()
        except Exception as e:
            return jsonify({"status":"error","message":str(e)}), 500
    else:
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

    if USE_SUPABASE:
        try:
            supabase.table("users").update({"avatar": rel}).eq("id", session['user_id']).execute()
        except Exception as e:
            return jsonify({"status":"error","message":str(e)}), 500
    else:
        conn=get_db()
        conn.execute('UPDATE users SET avatar=? WHERE id=?', (rel, session['user_id']))
        conn.commit(); conn.close()

    return jsonify({"status":"success","message":"Avatar diperbarui","avatar":rel})

# ---------- Supabase Bookmark & History ----------
@app.route('/api/bookmarks', methods=['GET'])
@login_required
def get_bookmarks():
    if not supabase:
        return jsonify({"status":"error","message":"Supabase belum terkonfigurasi"}), 500
    uid = session['user_id']
    try:
        res = supabase.table("bookmarks").select("*").eq("user_id", uid).order("created_at", desc=True).execute()
        return jsonify({"status":"success","data":res.data})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}), 500

@app.route('/api/bookmarks', methods=['POST'])
@login_required
def add_bookmark():
    if not supabase:
        return jsonify({"status":"error","message":"Supabase belum terkonfigurasi"}), 500
    data = request.get_json()
    uid = session['user_id']
    title = data.get('title','')
    url = data.get('url','')
    thumbnail = data.get('thumbnail','')
    episode = data.get('episode','')
    if not title or not url:
        return jsonify({"status":"error","message":"Title dan URL wajib"}), 400
    try:
        existing = supabase.table("bookmarks").select("id").eq("user_id", uid).eq("url", url).execute()
        if existing.data:
            return jsonify({"status":"error","message":"Sudah di-bookmark"}), 400
        supabase.table("bookmarks").insert({"user_id": uid, "title": title, "url": url, "thumbnail": thumbnail, "episode": episode}).execute()
        return jsonify({"status":"success","message":"Ditambahkan ke bookmark"})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}), 500

@app.route('/api/bookmarks', methods=['DELETE'])
@login_required
def remove_bookmark():
    if not supabase:
        return jsonify({"status":"error","message":"Supabase belum terkonfigurasi"}), 500
    data = request.get_json()
    uid = session['user_id']
    url = data.get('url','')
    try:
        supabase.table("bookmarks").delete().eq("user_id", uid).eq("url", url).execute()
        return jsonify({"status":"success","message":"Dihapus dari bookmark"})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}), 500

@app.route('/api/history', methods=['GET'])
@login_required
def get_history():
    if not supabase:
        return jsonify({"status":"error","message":"Supabase belum terkonfigurasi"}), 500
    uid = session['user_id']
    try:
        res = supabase.table("history").select("*").eq("user_id", uid).order("watched_at", desc=True).limit(100).execute()
        return jsonify({"status":"success","data":res.data})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}), 500

@app.route('/api/history', methods=['POST'])
@login_required
def add_history():
    if not supabase:
        return jsonify({"status":"error","message":"Supabase belum terkonfigurasi"}), 500
    data = request.get_json()
    uid = session['user_id']
    title = data.get('title','')
    url = data.get('url','')
    thumbnail = data.get('thumbnail','')
    episode = data.get('episode','')
    progress = data.get('progress', 0)
    if not title or not url:
        return jsonify({"status":"error","message":"Title dan URL wajib"}), 400
    try:
        existing = supabase.table("history").select("id").eq("user_id", uid).eq("url", url).execute()
        if existing.data:
            supabase.table("history").update({"title": title, "thumbnail": thumbnail, "episode": episode, "progress": progress, "watched_at": "now()"}).eq("id", existing.data[0]["id"]).execute()
        else:
            supabase.table("history").insert({"user_id": uid, "title": title, "url": url, "thumbnail": thumbnail, "episode": episode, "progress": progress}).execute()
        return jsonify({"status":"success","message":"Riwayat diperbarui"})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}), 500

@app.route('/api/history', methods=['DELETE'])
@login_required
def clear_history():
    if not supabase:
        return jsonify({"status":"error","message":"Supabase belum terkonfigurasi"}), 500
    uid = session['user_id']
    try:
        supabase.table("history").delete().eq("user_id", uid).execute()
        return jsonify({"status":"success","message":"Riwayat dihapus"})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}), 500

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
        # Title: prefer series name (h2 itemprop partOfSeries / .infolimit h2) over episode H1
        title_elem = soup.select_one('h2[itemprop="partOfSeries"], .infolimit h2, .infox h2, h1.entry-title')
        title = title_elem.text.strip() if title_elem else "Detail Vexora"
        # Clean episode suffix like " Episode 230 Tamat Subtitle Indonesia"
        title = re.sub(r'\s*Episode\s+\d+.*$', '', title, flags=re.IGNORECASE).strip()

        # Synopsis: prioritize real story in .desc.mindes / .desc over SEO spam in .entry-content
        SPAM_MARKERS = ["Download", "Nonton", "jangan lupa mengklik tombol like", "Mirrored", "PixelDrain", "Terabox", "360p", "480p", "1080p"]
        synopsis = ""
        for sel in ['.desc.mindes', '.desc', '.synopsis', '.synp', '[itemprop="description"]', '.entry-content', 'div.bixbox.synp']:
            el = soup.select_one(sel)
            if not el: continue
            txt = el.get_text(' ', strip=True)
            # skip spam blocks
            if any(m.lower() in txt.lower() for m in SPAM_MARKERS) and len(txt) > 200:
                # but .desc.mindes should never be spam, so this only hits entry-content
                continue
            if len(txt) < 40:
                continue
            # remove leading H3 duplicate title inside desc
            # el may contain <h3>The Emperor...</h3> + story -> strip first 60 chars if repeats title
            synopsis = txt.strip()
            # strip leading "Sinopsis" + duplicate H3 title inside .desc.mindes
            # e.g. "Sinopsis The Emperor of Myriad Realms The Emperor of Myriad Realms Tujuh..."
            for _ in range(3):
                low = synopsis.lower()
                if low.startswith("sinopsis"):
                    synopsis = synopsis[8:].lstrip(' :–—-').strip()
                    continue
                if low.startswith(title.lower()):
                    synopsis = synopsis[len(title):].lstrip(' :–—-.').strip()
                    continue
                break
            break
        if not synopsis:
            fallback = soup.select_one('.entry-content')
            synopsis = fallback.get_text(' ', strip=True).strip() if fallback else "Tidak ada sinopsis tersedia."
        # if synopsis still spam, try to clean spam sentences
        if any(m.lower() in synopsis.lower() for m in SPAM_MARKERS):
            parts = re.split(r'Download |Nonton ', synopsis)
            synopsis = parts[0].strip() if parts[0].strip() else synopsis
        for _ in range(3):
            low = synopsis.lower()
            if low.startswith("sinopsis"):
                synopsis = synopsis[8:].lstrip(' :–—-').strip()
                continue
            if low.startswith(title.lower()):
                synopsis = synopsis[len(title):].lstrip(' :–—-.').strip()
                continue
            break

        poster_elem = soup.select_one('.thumb img, .infox .fotoimg img, .poster img, .bigcontent .thumb img')
        poster = poster_elem.get('src') or poster_elem.get('data-src') if poster_elem else ""
        genres=[]
        # Only real genres from .genxed (avoid polluting with network/studio/country tags)
        for g in soup.select('.genxed a[rel="tag"], .genxed a[href*="/genres/"], .genre-info a[href*="/genres/"]'):
            g_text=g.text.strip()
            if g_text and g_text not in genres: genres.append(g_text)
        if not genres:
            # fallback but filter out meta-like tags
            for g in soup.select('.genxinf a[href*="/genres/"]'):
                g_text=g.text.strip()
                if g_text and g_text not in genres: genres.append(g_text)
        meta_data={}
        for row in soup.select('.info-content .spe span, .infox .spe span'):
            text=row.text.strip()
            if ':' in text:
                k,v=text.split(':',1)
                meta_data[k.strip().lower()]=v.strip()
        # Rating: from .rating strong like "Rating 7.89" or .rtp width
        rating_text=""
        rating_el = soup.select_one('.rating strong, .rt strong, [itemprop="ratingValue"]')
        if rating_el:
            rating_text = rating_el.get_text(strip=True)
        if not rating_text:
            rtb = soup.select_one('.rtb span')
            if rtb and rtb.get('style'):
                m=re.search(r'width:\s*([0-9.]+)%', rtb.get('style'))
                if m:
                    try:
                        pct=float(m.group(1))
                        rating_text=str(round(pct/10,2))
                    except: pass
        if rating_text:
            # extract numeric
            m=re.search(r'([0-9]+\.[0-9]+|[0-9]+)', rating_text)
            if m: meta_data['rating']=m.group(1)
        episodes=[]
        for ep in soup.select('.eplister ul li a, .episodelist ul li a'):
            ep_url=ep.get('href')
            if ep_url:
                ep_url=urljoin(target_url, ep_url)
                ep_title=ep.select_one('.epl-title, h3, h2, .playinfo h3')
                ep_text=ep.get_text(' ', strip=True)
                number_match=re.search(r'\b(?:eps?|episode)\s*[-.]?\s*(\d+)\b', ep_text, re.IGNORECASE)
                if not number_match:
                    number_match=re.search(r'episode[-_](\d+)', ep_url, re.IGNORECASE)
                episode_number=f"Episode {number_match.group(1)}" if number_match else "Episode"
                local_player_url=f"/player?url={quote(ep_url, safe='')}"
                episodes.append({"title":ep_title.get_text(' ', strip=True) if ep_title else ep_text,"number":episode_number,"url":local_player_url,"original_url":ep_url})
        return jsonify({"status":"success","title":title,"synopsis":synopsis,"poster":poster,"genres":genres,"meta":meta_data,"episodes":episodes})
    except Exception as e:
        return jsonify({"status":"error","message":str(e)}),500

def build_mock_with_more():
    out=[]
    for sec in MOCK_SECTIONS:
        s=dict(sec)
        s["more_url"]="/page/2"
        s["archive_url"]="https://anichin.moe/page/2/"
        out.append(s)
    return out

def parse_home_sections(soup, target_url):
    sections=[]
    block_elements=soup.select('.releases, .section, .widget, .bixbox, div[class*="venz"], div[class*="listupd"]')
    for block in block_elements:
        header_tag=block.select_one('h2, h3, h4, .hport span, .releases h2, .widget-title')
        if header_tag:
            section_title=header_tag.text.strip()
            if re.search(r'Episode\s+\d+|Subtitle\s+Indonesia', section_title, re.IGNORECASE): continue
            items=parse_anime_items(block)
            if items:
                more_url=None
                cand = block.select_one('a.next, a[rel="next"], .pagination a.next, .nav-links a.next, a.loadmore, a.more')
                if cand and cand.get('href'):
                    more_url=cand.get('href')
                else:
                    for a in block.select('a'):
                        txt=(a.get_text() or "").strip().lower()
                        if txt in ["selanjutnya","selanjutnya >","selengkapnya","lihat semua","more","next"] or "selanjutnya" in txt or "selengkapnya" in txt:
                            if a.get('href'):
                                more_url=a.get('href'); break
                if not more_url:
                    pag = block.select_one('.pagination a[href*="/page/"], .nav-links a[href*="/page/"]')
                    if pag and pag.get('href'): more_url=pag.get('href')
                if not more_url:
                    hl = header_tag if header_tag.name=='a' else header_tag.find_parent('a') or block.select_one('h2 a, h3 a, .widget-title a')
                    if hl and hl.get('href'): more_url=hl.get('href')
                if more_url and not more_url.startswith("http"):
                    more_url=urljoin("https://anichin.moe/", more_url)
                if not more_url:
                    low=section_title.lower()
                    if "drop" in low: more_url="https://anichin.moe/drop/"
                    elif "rilis" in low or "update" in low or "terbaru" in low: more_url="https://anichin.moe/page/2/"
                    elif "ongoing" in low: more_url="https://anichin.moe/ongoing/"
                    else: more_url="https://anichin.moe/page/2/"
                sections.append({"section_name":section_title,"total_items":len(items),"data":items,"more_url":more_url,"archive_url":more_url})
    return sections

@app.route('/api/home', methods=['GET'])
@cached_route(timeout=CACHE_TTL)
def api_home():
    target_url="https://anichin.moe/"
    t_start=time.time()
    def _fetch_html():
        try:
            r=requests.get(target_url, headers=HEADERS, timeout=12)
            return r if r.status_code==200 else None
        except Exception:
            return None
    try:
        # Scrape homepage + banner + schedule + genres serentak (paralel) via ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=4, thread_name_prefix='home') as ex:
            fh=ex.submit(_fetch_html)
            fb=ex.submit(scrape_banner_data)
            fs=ex.submit(scrape_schedule_data)
            fg=ex.submit(scrape_genres_data)
            resp=fh.result()
            banners=fb.result()
            schedule=fs.result()
            genres=fg.result()
        elapsed=round(time.time()-t_start,2)
        if resp is None:
            payload={"creator":"Vexalyn Developer","statusCode":200,"status":"success","elapsed_time":f"{elapsed} seconds","fallback":True,"sections":build_mock_with_more(),"banners":banners,"schedule":schedule,"genres":genres}
            return jsonify(payload)
        soup=BeautifulSoup(resp.text,'html.parser')
        sections=parse_home_sections(soup, target_url)
        if not sections:
            payload={"creator":"Vexalyn Developer","statusCode":200,"status":"success","elapsed_time":f"{elapsed} seconds","fallback":True,"sections":build_mock_with_more(),"banners":banners,"schedule":schedule,"genres":genres}
        else:
            payload={"creator":"Vexalyn Developer","statusCode":200,"status":"success","elapsed_time":f"{elapsed} seconds","sections":sections,"banners":banners,"schedule":schedule,"genres":genres}
        # Warm related caches so /api/banner & /api/schedule are instant on next call
        try:
            write_db_cache('scraper.banner', {"creator":"Vexora Developer","statusCode":200,"status":"success","total_banners":len(banners),"banners":banners})
            write_db_cache('scraper.schedule', {"creator":"Vexora Developer","statusCode":200,"status":"success","total_days":len(schedule),"schedule":schedule})
        except Exception:
            pass
        return jsonify(payload)
    except Exception as e:
        return jsonify({"creator":"Vexalyn Developer","statusCode":200,"status":"success","elapsed_time":"0 seconds","fallback":True,"sections":build_mock_with_more(),"banners":MOCK_BANNERS,"schedule":[],"genres":[],"error":str(e)})

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

@app.route('/api/all', methods=['GET'])
def api_all():
    page = request.args.get('page', 1, type=int)
    if page < 1:
        page = 1
    target_url = "https://anichin.moe/"
    if page > 1:
        target_url = f"https://anichin.moe/page/{page}/"
    t_start = time.time()
    try:
        response = requests.get(target_url, headers=HEADERS, timeout=12)
        elapsed = round(time.time() - t_start, 2)
        if response.status_code != 200:
            return jsonify({"creator": "Vexalyn Developer", "statusCode": 200, "status": "success", "elapsed_time": f"{elapsed} seconds", "fallback": True, "current_page": 1, "total_pages": 1, "data": []})
        soup = BeautifulSoup(response.text, 'html.parser')
        sections = parse_home_sections(soup, target_url)
        anime_list = []
        for sec in sections:
            anime_list.extend(sec.get('data', []))
        if not anime_list:
            anime_list = MOCK_SECTIONS[0]["data"]
        total_pages = 1
        if page == 1:
            total_pages = get_last_page(soup)
        else:
            try:
                r1 = requests.get("https://anichin.moe/", headers=HEADERS, timeout=8)
                if r1.status_code == 200:
                    s1 = BeautifulSoup(r1.text, 'html.parser')
                    total_pages = get_last_page(s1)
            except Exception:
                total_pages = page
        return jsonify({
            "creator": "Vexalyn Developer",
            "statusCode": 200,
            "status": "success",
            "elapsed_time": f"{elapsed} seconds",
            "total_data": len(anime_list),
            "data": anime_list,
            "current_page": page,
            "total_pages": total_pages
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/banner', methods=['GET'])
def api_banner():
    cached, stale = read_db_cache('scraper.banner')
    if cached is not None:
        if stale:
            refresh_db_cache_async('scraper.banner', lambda: {"creator":"Vexora Developer","statusCode":200,"status":"success","elapsed_time":"background","total_banners":len(scrape_banner_data()),"banners":scrape_banner_data()})
        return jsonify(cached)
    t_start=time.time()
    banners=scrape_banner_data()
    elapsed=round(time.time()-t_start,2)
    payload={"creator":"Vexalyn Developer","statusCode":200,"status":"success","elapsed_time":f"{elapsed} seconds","total_banners":len(banners),"banners":banners}
    write_db_cache('scraper.banner', payload)
    return jsonify(payload)

@app.route('/api/schedule', methods=['GET'])
def api_schedule():
    cached, stale = read_db_cache('scraper.schedule')
    if cached is not None:
        if stale:
            refresh_db_cache_async('scraper.schedule', lambda: {"creator":"Vexora Developer","statusCode":200,"status":"success","elapsed_time":"background","total_days":len(scrape_schedule_data()),"schedule":scrape_schedule_data()})
        return jsonify(cached)
    t_start=time.time()
    data=scrape_schedule_data()
    elapsed=round(time.time()-t_start,2)
    payload={"creator":"Vexalyn Developer","statusCode":200,"status":"success","elapsed_time":f"{elapsed} seconds","total_days":len(data),"schedule":data}
    write_db_cache('scraper.schedule', payload)
    return jsonify(payload)

def scrape_genres_data():
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
            return FALLBACK_GENRES
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
            return FALLBACK_GENRES
        return genres_list
    except Exception:
        return FALLBACK_GENRES

GENRE_COUNT_TTL = int(os.environ.get("GENRE_COUNT_TTL", "3600"))

def get_last_page(soup):
    max_page = 1
    for a in soup.select('a[href*="page/"]'):
        href = a.get('href', '')
        import re
        m = re.search(r'/page/(\d+)/', href)
        if m:
            page = int(m.group(1))
            if page > max_page:
                max_page = page
    return max_page

def scrape_genre_count(slug):
    try:
        clean = slug.strip().lower().replace(" ", "-")
        url = f"https://anichin.moe/genres/{clean}/"
        r = requests.get(url, headers=HEADERS, timeout=12)
        if r.status_code != 200:
            return 0
        soup = BeautifulSoup(r.text, 'html.parser')
        items = parse_anime_items(soup)
        first_page_count = len(items) if items else 0
        last_page = get_last_page(soup)
        if last_page <= 1:
            return first_page_count
        # Fetch last page to get exact count on final page
        last_url = f"https://anichin.moe/genres/{clean}/page/{last_page}/"
        lr = requests.get(last_url, headers=HEADERS, timeout=12)
        if lr.status_code != 200:
            return first_page_count * last_page
        lsoup = BeautifulSoup(lr.text, 'html.parser')
        last_items = parse_anime_items(lsoup)
        last_page_count = len(last_items) if last_items else 0
        return (last_page - 1) * first_page_count + last_page_count
    except Exception:
        return 0

def scrape_genres_with_counts():
    genres=scrape_genres_data()
    if not genres:
        return []
    def _worker(g):
        return {"name": g["name"], "slug": g["slug"], "count": scrape_genre_count(g["slug"])}
    try:
        with ThreadPoolExecutor(max_workers=8, thread_name_prefix='genre-count') as ex:
            out=list(ex.map(_worker, genres))
    except Exception:
        out=[{"name": g["name"], "slug": g["slug"], "count": 0} for g in genres]
    return out

@app.route('/api/genres', methods=['GET'])
@cached_route(timeout=CACHE_TTL)
def api_all_genres():
    cached, stale = read_db_cache('scraper.genre_counts', GENRE_COUNT_TTL)
    if cached is not None:
        if stale:
            refresh_db_cache_async('scraper.genre_counts', scrape_genres_with_counts)
        return jsonify({"status":"success","total":len(cached),"data":cached})
    data=scrape_genres_with_counts()
    write_db_cache('scraper.genre_counts', data)
    return jsonify({"status":"success","total":len(data),"data":data})

@app.route('/api/genre/<path:genre_slug>', methods=['GET'])
def api_genre(genre_slug):
    clean_genre = genre_slug.strip().lower().replace(" ", "-")
    page = request.args.get('page', 1, type=int)
    if page < 1:
        page = 1
    target_url = f"https://anichin.moe/genres/{clean_genre}/"
    if page > 1:
        target_url = f"https://anichin.moe/genres/{clean_genre}/page/{page}/"
    t_start = time.time()
    try:
        response = requests.get(target_url, headers=HEADERS, timeout=12)
        elapsed = round(time.time() - t_start, 2)
        if response.status_code != 200:
            filtered = []
            for sec in MOCK_SECTIONS:
                for item in sec["data"]:
                    if clean_genre in item["title"].lower() or True:
                        filtered.append(item)
                    if len(filtered) >= 12:
                        break
            return jsonify({"creator": "Vexalyn Developer", "statusCode": 200, "status": "success", "genre": clean_genre, "elapsed_time": f"{elapsed} seconds", "fallback": True, "total_data": len(filtered[:12]), "data": filtered[:12], "current_page": 1, "total_pages": 1})
        soup = BeautifulSoup(response.text, 'html.parser')
        anime_list = parse_anime_items(soup)
        if not anime_list:
            anime_list = MOCK_SECTIONS[0]["data"]
        # Get total pages from pagination on first page
        total_pages = 1
        if page == 1:
            total_pages = get_last_page(soup)
        else:
            # For other pages, we need to fetch page 1 to get total pages
            # This is a quick fetch; could be optimized by caching
            try:
                first_page_url = f"https://anichin.moe/genres/{clean_genre}/"
                r1 = requests.get(first_page_url, headers=HEADERS, timeout=8)
                if r1.status_code == 200:
                    s1 = BeautifulSoup(r1.text, 'html.parser')
                    total_pages = get_last_page(s1)
            except Exception:
                total_pages = page  # fallback
        return jsonify({
            "creator": "Vexalyn Developer",
            "statusCode": 200,
            "status": "success",
            "genre": clean_genre,
            "elapsed_time": f"{elapsed} seconds",
            "total_data": len(anime_list),
            "data": anime_list,
            "current_page": page,
            "total_pages": total_pages
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/terbaru', methods=['GET'])
def api_terbaru():
    page = request.args.get('page', 1, type=int)
    if page < 1:
        page = 1
    target_url = "https://anichin.moe/"
    if page > 1:
        target_url = f"https://anichin.moe/page/{page}/"
    t_start = time.time()
    try:
        response = requests.get(target_url, headers=HEADERS, timeout=12)
        elapsed = round(time.time() - t_start, 2)
        if response.status_code != 200:
            return jsonify({"creator": "Vexalyn Developer", "statusCode": 200, "status": "success", "elapsed_time": f"{elapsed} seconds", "fallback": True, "current_page": 1, "total_pages": 1, "data": []})
        soup = BeautifulSoup(response.text, 'html.parser')
        sections = parse_home_sections(soup, target_url)
        anime_list = []
        for sec in sections:
            anime_list.extend(sec.get('data', []))
        if not anime_list:
            anime_list = MOCK_SECTIONS[0]["data"]
        # Sort by episode number desc (latest first)
        import re
        def ep_num(x):
            m = re.search(r'(\d+)', x.get('episode') or '')
            return int(m.group(1)) if m else 0
        anime_list.sort(key=ep_num, reverse=True)
        total_pages = 1
        if page == 1:
            total_pages = get_last_page(soup)
        else:
            try:
                r1 = requests.get("https://anichin.moe/", headers=HEADERS, timeout=8)
                if r1.status_code == 200:
                    s1 = BeautifulSoup(r1.text, 'html.parser')
                    total_pages = get_last_page(s1)
            except Exception:
                total_pages = page
        return jsonify({
            "creator": "Vexalyn Developer",
            "statusCode": 200,
            "status": "success",
            "elapsed_time": f"{elapsed} seconds",
            "total_data": len(anime_list),
            "data": anime_list,
            "current_page": page,
            "total_pages": total_pages
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/terbaru')
def terbaru_page():
    return render_template('terbaru.html')

# ---------- Custom error handlers ----------
ERROR_PAGES = {
    403: {"title": "Wah, Dicekal Nih!", "message": "Tenang, ini bukan salah kamu sepenuhnya. Aksesnya keblokir sama penjaga portal, cuy. Balik ke Beranda aja yuk."},
    404: {"title": "Waduh, Nyasar!", "message": "Kayaknya halaman yang kamu cari lagi ngumpet di dimensi lain, cuy. Atau emang gak ada dari sananya."},
    500: {"title": "Sistem Lagi Rewel", "message": "Server lagi panic mode sebentar. Tim Vexora lagi beresin dalam senyap. Coba refresh atau balik ke Beranda."},
}

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, **ERROR_PAGES[403]), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, **ERROR_PAGES[404]), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, **ERROR_PAGES[500]), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
