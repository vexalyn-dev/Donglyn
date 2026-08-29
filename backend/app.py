# backend/app.py — Donglyn Flask API (Lightweight, JSON-only)
import sys, asyncio, time, re, os, json
from functools import wraps

from flask import Flask, request, jsonify, Response

sys.path.insert(0, os.path.dirname(__file__))

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, unquote, urljoin, urlparse
import brotli

try:
    from banner import scrape_banner
    HAS_BANNER = True
except ImportError:
    HAS_BANNER = False

try:
    from detail import scrape_detail
    HAS_DETAIL = True
except ImportError:
    HAS_DETAIL = False

try:
    from search import scrape_search
    HAS_SEARCH = True
except ImportError:
    HAS_SEARCH = False

try:
    from schedule import main as schedule_main
    HAS_SCHEDULE = True
except ImportError:
    HAS_SCHEDULE = False

try:
    from genre import scrape_all_genres
    HAS_GENRE = True
except ImportError:
    HAS_GENRE = False

try:
    from home import scrape_homepage
    HAS_HOME = True
except ImportError:
    HAS_HOME = False

try:
    from stream import resolve_episode_url_stable
    HAS_STREAM = True
except ImportError:
    HAS_STREAM = False

try:
    from video_engine import resolve_okru, resolve_dailymotion, resolve_streamwish, resolve_flickr, bypass_shortlink
    HAS_VIDEO_ENGINE = True
except ImportError:
    HAS_VIDEO_ENGINE = False
    resolve_okru = None
    resolve_dailymotion = None
    resolve_streamwish = None
    resolve_flickr = None
    bypass_shortlink = None

APP_START_TIME = time.time()

app = Flask(__name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static')
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://anichin.moe/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ---------- Helpers ----------
def error_response(message: str, status_code: int = 500):
    return jsonify({
        "statusCode": status_code,
        "status": "error",
        "message": message,
    }), status_code


def success_response(data: dict, elapsed: float):
    return jsonify({
        "creator": "Vexalyn Developer",
        "statusCode": 200,
        "status": "success",
        "data": data,
        "elapsed_time": f"{elapsed:.2f} seconds",
    })


def async_to_sync(coro_fn, *args, **kwargs):
    """Run async function synchronously."""
    return asyncio.run(coro_fn(*args, **kwargs))


# ---------- Health ----------
@app.route('/api/health')
def health():
    return jsonify({"status": "ok", "uptime": round(time.time() - APP_START_TIME, 1)})


# ---------- Home ----------
@app.route('/api/home')
def api_home():
    t_start = time.time()
    try:
        if not HAS_HOME:
            return error_response("Home scraper not available")
        data = async_to_sync(scrape_homepage)
        if not data:
            return error_response("Failed to scrape homepage")
        elapsed = round(time.time() - t_start, 2)
        return success_response(data, elapsed)
    except Exception as e:
        return error_response(f"Home scrape error: {str(e)}")


# ---------- Banner ----------
@app.route('/api/banner')
def api_banner():
    t_start = time.time()
    try:
        if not HAS_BANNER:
            return error_response("Banner scraper not available")
        # scrape_banner() returns a dict with "banners" key
        result = async_to_sync(scrape_banner)
        banners = []
        if isinstance(result, dict):
            banners = result.get("banners", [])
        elapsed = round(time.time() - t_start, 2)
        return success_response({"banners": banners}, elapsed)
    except Exception as e:
        return error_response(f"Banner scrape error: {str(e)}")


# ---------- Schedule ----------
@app.route('/api/schedule')
def api_schedule():
    day = request.args.get('day', 'all')
    t_start = time.time()
    try:
        if not HAS_SCHEDULE:
            return error_response("Schedule scraper not available")
        result = async_to_sync(schedule_main, day)
        if not result:
            return error_response("Failed to scrape schedule")
        elapsed = round(time.time() - t_start, 2)
        return success_response(result, elapsed)
    except Exception as e:
        return error_response(f"Schedule scrape error: {str(e)}")


# ---------- Genres ----------
@app.route('/api/genres')
def api_genres():
    t_start = time.time()
    try:
        if not HAS_GENRE:
            return error_response("Genre scraper not available")
        result = async_to_sync(scrape_all_genres)
        if not result:
            return error_response("Failed to scrape genres")
        elapsed = round(time.time() - t_start, 2)
        return success_response(result, elapsed)
    except Exception as e:
        return error_response(f"Genre scrape error: {str(e)}")


# ---------- Search ----------
@app.route('/api/search', methods=['POST'])
def api_search():
    data = request.get_json() or {}
    query = data.get('q', '').strip()
    t_start = time.time()
    try:
        if not HAS_SEARCH:
            return error_response("Search scraper not available")
        result = async_to_sync(scrape_search, query)
        if not result:
            return error_response(f"No results for '{query}'")
        elapsed = round(time.time() - t_start, 2)
        return success_response(result, elapsed)
    except Exception as e:
        return error_response(f"Search error: {str(e)}")


# ---------- Detail ----------
@app.route('/api/detail-data', methods=['POST'])
def api_detail():
    data = request.get_json() or {}
    url = data.get('url', '').strip()
    t_start = time.time()
    try:
        if not url:
            return error_response("URL is required", 400)
        if not HAS_DETAIL:
            return error_response("Detail scraper not available")
        result = async_to_sync(scrape_detail, url)
        if not result:
            return error_response("Failed to scrape detail page")
        elapsed = round(time.time() - t_start, 2)
        return success_response(result, elapsed)
    except Exception as e:
        return error_response(f"Detail scrape error: {str(e)}")


# ---------- Genre Single ----------
@app.route('/api/genre/<path:genre_slug>')
def api_genre_single(genre_slug):
    t_start = time.time()
    try:
        # Reuse home scraper with genre filter
        from home import scrape_homepage
        result = async_to_sync(scrape_homepage)
        if not result:
            return error_response("Failed to load content")
        # Filter by genre slug
        sections = result.get("sections", [])
        filtered = []
        for section in sections:
            items = section.get("data", [])
            for item in items:
                if genre_slug.lower() in item.get("url", "").lower() or genre_slug.lower() in item.get("title", "").lower():
                    filtered.append(item)
        elapsed = round(time.time() - t_start, 2)
        return success_response({"genre": genre_slug, "data": filtered[:20]}, elapsed)
    except Exception as e:
        return error_response(f"Genre error: {str(e)}")


# ---------- Stream (Video Engine) ----------
@app.route('/api/stream', methods=['POST'])
def api_stream():
    data = request.get_json() or {}
    episode_url = data.get('url', '').strip()
    server = data.get('server', 'Okru').capitalize()

    if not episode_url:
        return error_response("url required", 400)

    t_start = time.time()

    try:
        if not HAS_STREAM:
            return error_response("Stream resolver not available")

        # Resolve slug to full URL
        full_url = resolve_episode_url_stable(episode_url) or episode_url

        # Try specific adapter first, then fallback
        result = None

        server_lower = server.lower()

        if 'okru' in server_lower:
            if HAS_VIDEO_ENGINE and resolve_okru:
                result = asyncio.run(resolve_okru(full_url))
        elif 'dailymotion' in server_lower or server_lower == 'dm':
            if HAS_VIDEO_ENGINE and resolve_dailymotion:
                result = asyncio.run(resolve_dailymotion(full_url))
        elif 'streamwish' in server_lower:
            if HAS_VIDEO_ENGINE and resolve_streamwish:
                result = asyncio.run(resolve_streamwish(full_url))
        elif 'flickr' in server_lower:
            if HAS_VIDEO_ENGINE and resolve_flickr:
                result = asyncio.run(resolve_flickr(full_url))

        # Fallback: try all adapters
        if not result or not result.get("video_url"):
            fallback_adapters = [
                ("Okru", resolve_okru),
                ("Dailymotion", resolve_dailymotion),
                ("StreamWish", resolve_streamwish),
                ("Flickr", resolve_flickr),
            ]
            for name, adapter_fn in fallback_adapters:
                if adapter_fn and HAS_VIDEO_ENGINE:
                    try:
                        r = asyncio.run(adapter_fn(full_url))
                        if r and r.get("video_url"):
                            result = r
                            server = name
                            break
                    except Exception:
                        continue

        if not result or not result.get("video_url"):
            return error_response(f"All servers failed. Last error: {result.get('error', 'unknown')}" if result else "No servers available", 500)

        elapsed = round(time.time() - t_start, 2)
        result['elapsed_time'] = f"{elapsed} seconds"
        result['statusCode'] = 200
        result['status'] = 'success'
        return jsonify(result)

    except Exception as e:
        return error_response(f"Stream error: {str(e)}", 500)


# ---------- Proxy Endpoints ----------
@app.route('/api/proxy-okru')
def proxy_okru():
    target = request.args.get('url', '')
    if not target:
        return error_response("url required", 400)
    try:
        r = requests.get(target, headers={
            "User-Agent": HEADERS["User-Agent"],
            "Referer": "https://ok.ru/",
        }, timeout=15, allow_redirects=True)
        return Response(r.content, status=r.status_code,
                       content_type=r.headers.get('content-type', 'text/html'),
                       headers={'Access-Control-Allow-Origin': '*'})
    except Exception as e:
        return error_response(str(e), 502)


@app.route('/api/proxy-dm')
def proxy_dailymotion():
    target = request.args.get('url', '')
    if not target:
        return error_response("url required", 400)
    try:
        r = requests.get(target, headers={
            "User-Agent": HEADERS["User-Agent"],
            "Referer": "https://www.dailymotion.com/",
        }, timeout=15, allow_redirects=True)
        body = r.content
        if r.headers.get('Content-Encoding') == 'br':
            try:
                body = brotli.decompress(body)
            except Exception:
                pass
        return Response(body, status=r.status_code,
                       content_type=r.headers.get('content-type', 'text/html'),
                       headers={'Access-Control-Allow-Origin': '*'})
    except Exception as e:
        return error_response(str(e), 502)


@app.route('/api/proxy')
def proxy_generic():
    """Generic proxy for any server that blocks direct iframe."""
    target = request.args.get('url', '')
    referer = request.args.get('referer', '')
    if not target:
        return error_response("url required", 400)
    try:
        r = requests.get(target, headers={
            "User-Agent": HEADERS["User-Agent"],
            "Referer": referer or "https://anichin.moe/",
        }, timeout=15, allow_redirects=True)
        body = r.content
        if r.headers.get('Content-Encoding') == 'br':
            try:
                body = brotli.decompress(body)
            except Exception:
                pass
        return Response(body, status=r.status_code,
                       content_type=r.headers.get('content-type', 'text/html'),
                       headers={'Access-Control-Allow-Origin': '*'})
    except Exception as e:
        return error_response(str(e), 502)


# ---------- Static assets (for legacy compatibility) ----------
@app.route('/asset/<path:filename>')
@app.route('/assets/<path:filename>')
def serve_asset(filename):
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static')
    asset_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'asset')
    for d in [static_dir, asset_dir]:
        path = os.path.join(d, filename)
        if os.path.exists(path):
            return send_file_from_path(path)
    return jsonify({"error": "not found"}), 404


def send_file_from_path(path):
    import mimetypes
    mime_type, _ = mimetypes.guess_type(path)
    from flask import send_file as sf
    return sf(path, mimetype=mime_type or 'application/octet-stream')


@app.route('/favicon.ico')
def favicon():
    return send_file_from_path(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static', 'favicon.svg'))


# ---------- Legacy page routes (still serve HTML for backward compat) ----------
@app.route('/')
def index():
    return jsonify({"message": "Use /api/home for data. Next.js frontend handles rendering."})


@app.route('/search')
def search_page():
    query = request.args.get('q', '')
    return jsonify({"query": query, "message": "Use /api/search for data."})


@app.route('/detail')
def detail_page():
    url = request.args.get('url', '')
    return jsonify({"url": url, "message": "Use /api/detail-data for data."})


@app.route('/player')
def player_page():
    return jsonify({"message": "Use /api/stream for video data."})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
