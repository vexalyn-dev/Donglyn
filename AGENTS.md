# Donglyn — AGENTS.md

## Quick Start

```bash
pip install -r requirements.txt
playwright install chromium
npm install                    # only if changing Tailwind CSS
python run.py
```

Rebuild CSS after editing `frontend/src/input.css`:
```bash
npx tailwindcss -i ./frontend/src/input.css -o ./frontend/static/css/output.css --minify --postcss
```
or watch mode: `npm run dev`.

## Project Structure

```
Donglyn/
├── backend/                  # Python backend
│   ├── app.py                # Main Flask app (all routes, scraping, auth)
│   ├── banner.py             # Banner/scraping logic
│   ├── detail.py             # Detail page scraping
│   ├── episode.py            # Episode/page scraping
│   ├── genre.py              # Genre scraping
│   ├── genre_filter.py       # Genre filter logic
│   ├── home.py               # Home page scraping
│   ├── schedule.py           # Schedule scraping
│   ├── search.py             # Search scraping
│   ├── core/
│   │   ├── browser.py        # Playwright browser config
│   │   └── __init__.py
│   └── users.db              # SQLite database (or use Supabase)
├── frontend/                 # Frontend assets
│   ├── templates/            # Jinja2 HTML templates (20 files)
│   ├── static/
│   │   ├── css/              # Compiled CSS (output.css — DO NOT EDIT)
│   │   ├── js/               # JavaScript (ui.js, sync.js)
│   │   ├── src/              # Tailwind source (input.css)
│   │   ├── audio/            # Sound effects
│   │   └── uploads/          # User uploads
│   └── asset/                # Images (logo.png, favicon.png, etc.)
├── run.py                    # Entry point (python run.py)
├── requirements.txt
├── package.json
├── .env                      # Environment variables
└── render.yaml               # Render.com deployment config
```

## Commands

| Task | Command |
|---|---|
| Run dev server | `python run.py` |
| Rebuild CSS | `npx tailwindcss -i ./frontend/src/input.css -o ./frontend/static/css/output.css --minify --postcss` |
| Watch CSS (dev) | `npm run dev` |
| Production (Render) | `gunicorn backend.app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
| Install Playwright browsers | `playwright install chromium` |

## Environment Variables

Copy `.env.example` to `.env` and fill in at minimum:
- `SECRET_KEY` — Flask session secret
- `SUPABASE_URL` / `SUPABASE_KEY` — or skip for SQLite
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` — optional Google OAuth
- `RESEND_API_KEY` / `RESEND_FROM_EMAIL` — optional email OTP
- `FONNTE_TOKEN` — optional WhatsApp OTP
- `DEV_SECRET_KEY` — default `Donglyn_DEV_SECRET_2026`; used by dev panel easter egg

## Icons (Critical)

- **All icons use Lucide** via `<i data-lucide="icon-name"></i>` + `lucide.createIcons()` called in `DOMContentLoaded` in `base.html` (~line 522).
- Font Awesome **brands** CDN is kept **only** for social icons (Instagram/TikTok/GitHub) in the footer.
- **Never** use `fa-solid fa-*` or `class="fas fa-*"` — these are broken and will not render.
- Animated icon classes (from lucide-animated.com style): `icon-bounce`, `icon-pulse`, `icon-spin-hover`, `icon-shimmer`, `icon-swing`. Apply to `<i>` elements that need hover animation.
- **Fix helper** for malformed `data-lucide` attributes where Tailwind classes leaked outside `class=""`:
  ```python
  import re
  c = re.sub(r'<i\s+data-lucide="([^"]+)"\s+([whtfblc][^>]*)>',
             lambda m: f'<i data-lucide="{m.group(1)}" class="{m.group(2).strip()}"></i>', c)
  ```
- **Fix helper** for double `class="class="` injection from previous edit bugs:
  ```python
  c = re.sub(r'class="class="([^"]*)"\"', r'class="\1"', c)
  ```

## Template Conventions

- Child pages place raw CSS inside `{% block extra_css %}` and raw JS inside `{% block extra_js %}` — no wrapper tags. `base.html` injects them inside `<style>` / `<script>` tags automatically.
- Some templates (terbaru, search, schedule) have inline `<script>` in `extra_css` blocks for nav-indicator logic. This is intentional — it runs before the main body script.
- **No inline `style="..."` attributes** in templates. Add rules to `static/src/input.css` and rebuild.
- **Always add `decoding="async"`** to `<img loading="lazy">` tags to suppress browser lazy-loading warnings.
- **Splash screen** (`#splash`) is in `base.html` lines 163–175. It auto-hides after 800ms via JS. The `#splashLogoImg` has an `onerror` fallback to `#splashFallback`.

## Lang System Gotcha

- `base.html` declares `let currentLang = ...` (line ~385) — this is the **canonical** declaration.
- **`index.html` uses `donglynLang`** (line ~1044) to avoid the duplicate `currentLang` declaration error. Any new template with lang logic should use a unique variable name.

## Dev Panel (Easter Egg)

- Hidden behind `#devSecretModal` and `#devCyberOverlay` in `base.html` (lines ~302–311) and **also duplicated in `index.html`** (lines ~170, ~451), both with `style="display:none"` — they only appear when triggered.
- Triggered by: clicking the logo 7 times (`#donglynSecretTrigger`), pressing **Ctrl+Shift+V**, or typing the sequence `d-o-n-g-l-y-n`.
- Passcode verified server-side against `DEV_SECRET_KEY` env var (default: `Donglyn_DEV_SECRET_2026`).
- Admin check: `is_dev_admin()` in `app.py:643`; compares username against `DEV_PANEL_ADMINS` env var.

## Key Code Patterns

- **Scrape fallback**: every scraping function returns `MOCK_*` constants if the request fails or parsing yields nothing. The site runs offline once cached.
- **Cache layer**: two-tier — in-memory `_cache` (TTL via `cache_get`/`cache_set`) + SQLite `cache` table. Cache key format: `"route:" + request.full_path`.
- **Player iframe resolution**: `scrape_stream_token_async()` in `app.py` navigates `/stream/TOKEN` URLs through a chain of iframes to extract the final video URL. Called via `asyncio.run()` from synchronous Flask handlers.
- **Auth fallback chain**: Supabase → SQLite. All auth functions check `USE_SUPABASE` at runtime.
- **Dev panel access**: admin users matched against `DEV_PANEL_ADMINS` env var. Check `session['is_admin']` or call `is_dev_admin()`.

## Files to Edit First When Investigating

1. `backend/app.py` — all routes and business logic
2. `frontend/templates/base.html` — layout, nav, shared CSS, splash screen, lang system
3. `frontend/templates/index.html` — standalone home page (does NOT extend base.html); contains its own dev panel copy
4. `frontend/src/input.css` — Tailwind source (rebuild after editing)
5. `backend/core/browser.py` — Playwright browser config
6. `frontend/static/js/ui.js` — shared client-side JS (dropdowns, mobile menu, search)

## Linting Note

VS Code shows CSS errors on lines containing `{% block extra_css %}` inside `<style>` tags. This is a **false positive** — the linter doesn't understand Jinja2. `.vscode/settings.json` disables CSS validation for HTML to suppress these warnings. If warnings persist, reload the VS Code window (`Ctrl+Shift+P` → `Developer: Reload Window`).
