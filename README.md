<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/VexalynDeveloper/Donglyn/main/frontend/public/logo.png">
  <img src="https://raw.githubusercontent.com/VexalynDeveloper/Donglyn/main/frontend/public/logo.png" alt="Donglyn Logo" width="280" height="auto">
</picture>

# **Donglyn**

### Premium Donghua Streaming Platform

[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38BDF8?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Playwright](https://img.shields.io/badge/Playwright-1.40+-2ead33?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

**Donglyn** adalah platform streaming donghua (animasi China) premium dengan antarmuka modern, sinematik, dan responsif. Menggunakan Next.js + Flask API yang terpisah, dengan engine streaming Playwright untuk menelusuri server video (Okru, Dailymotion, StreamWish, Flickr).

<div align="center">

[🌐 Demo](https://donglyn.vercel.app) · [📖 Dokumentasi](./docs) · [🐛 Report Bug](https://github.com/VexalynDeveloper/Donglyn/issues)

</div>

---

## ✨ Fitur

| Fitur | Deskripsi |
|-------|-----------|
| 🎬 **Cinematic Hero** | Banner slider dengan efek gradient sinematik |
| 🔍 **Real-time Search** | Pencarian langsung dari anichin.moe |
| 📅 **Jadwal Rilis** | Schedule episode terbaru per hari |
| 🏷️ **Genre Filter** | Filter berdasarkan genre donghua |
| 🎥 **Multi-server Streaming** | Okru, Dailymotion, StreamWish, Flickr |
| 🔐 **Multi-auth** | Email, Google OAuth, WhatsApp OTP |
| 🔖 **Bookmark & Riwayat** | Simpan & lanjutkan tontonan |
| 🌍 **Multi-language** | Indonesia, English, Japanese, Chinese |
| 📱 **Fully Responsive** | Mobile-first, optimized untuk semua device |
| 🎨 **Premium Dark UI** | Dark theme dengan accent crimson red |
| ⚡ **Fast & Optimized** | Next.js static generation + lazy loading |

---

## 🛠️ Tech Stack

### Frontend
<table>
<tr>
<td><b>Framework</b></td><td>Next.js 14 (App Router)</td>
</tr>
<tr>
<td><b>Language</b></td><td>TypeScript 5</td>
</tr>
<tr>
<td><b>Styling</b></td><td>Tailwind CSS 3.4</td>
</tr>
<tr>
<td><b>UI Library</b></td><td>Lucide Icons + Swiper 11</td>
</tr>
<tr>
<td><b>Font</b></td><td>Inter + Bebas Neue (Google Fonts)</td>
</tr>
</table>

### Backend
<table>
<tr>
<td><b>Framework</b></td><td>Flask 3.0</td>
</tr>
<tr>
<td><b>Language</b></td><td>Python 3.11+</td>
</tr>
<tr>
<td><b>Scraping</b></td><td>Playwright (async) + BeautifulSoup4</td>
</tr>
<tr>
<td><b>Database</b></td><td>Supabase (PostgreSQL) + SQLite fallback</td>
</tr>
<tr>
<td><b>Auth</b></td><td>Google OAuth 2.0 + Phone OTP (Fonnte/Resend)</td>
</tr>
<tr>
<td><b>Deployment</b></td><td>Render.com (dual service)</td>
</tr>
</table>

### Video Engine
<table>
<tr>
<td><b>Adapters</b></td><td>Okru, Dailymotion, StreamWish, Flickr</td>
</tr>
<tr>
<td><b>Method</b></td><td>Playwright headless browser + iframe chain resolution</td>
</tr>
<tr>
<td><b>Proxy</b></td><td>CORS-enabled proxy endpoints (okru, dm, generic)</td>
</tr>
</table>

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                           │
│                                                                     │
│   ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐   │
│   │  Next.js 14  │  │  React 18    │  │  TypeScript 5          │   │
│   │  App Router  │  │  Components  │  │  Type-safe APIs        │   │
│   └──────┬───────┘  └──────┬───────┘  └──────────┬─────────────┘   │
│          │                 │                      │                 │
│   ┌──────▼───────┐  ┌──────▼───────┐  ┌──────────▼─────────────┐   │
│   │  Tailwind    │  │  Lucide +    │  │  Swiper 11             │   │
│   │  CSS v3      │  │  Icons       │  │  Banner Slider         │   │
│   └──────────────┘  └──────────────┘  └────────────────────────┘   │
│                                                                     │
└──────────────────────────┬──────────────────────────────────────────┘
                           │  fetch() / API calls
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FLASK API BACKEND (:5000)                     │
│                                                                     │
│   ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐   │
│   │  /api/home   │  │  /api/search │  │  /api/detail-data      │   │
│   │  /api/banner │  │  /api/schedule│ │  /api/genres           │   │
│   │  /api/stream │  │  /api/proxy  │  │  /api/auth/*           │   │
│   └──────┬───────┘  └──────┬───────┘  └──────────┬─────────────┘   │
│          │                 │                      │                 │
│   ┌──────▼──────────────────▼──────────────────────▼─────────────┐  │
│   │                    SCRAPER ENGINE                            │  │
│   │  home.py  │  banner.py  │  detail.py  │  search.py           │  │
│   │  schedule │  genre.py   │  stream.py  │  core/               │  │
│   └──────┬──────────────────┬──────────────────┬─────────────────┘  │
│          │                  │                  │                     │
│   ┌──────▼───────┐  ┌───────▼──────┐  ┌─────▼───────────────┐      │
│   │  Anichin    │  │  Video      │  │  External APIs       │      │
│   │  .moe       │  │  Player     │  │  (Google, Resend,    │      │
│   │  (Source)   │  │  Iframes    │  │   Fonnte, Supabase)  │      │
│   └─────────────┘  └──────────────┘  └─────────────────────┘      │
│                                                                     │
└──────────────────────────┬──────────────────────────────────────────┘
                           │  asyncio.run()
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     VIDEO STREAMING ENGINE                          │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐  │
│   │  backend/video_engine/adapters/                             │  │
│   │                                                             │  │
│   │  ┌──────────┐  ┌──────────────┐  ┌────────────┐           │  │
│   │  │ okru.py  │  │dailymotion.py│  │streamwish.py│          │  │
│   │  │ (Okru)   │  │ (Dailymotion)│  │ (StreamWish)│          │  │
│   │  └────┬─────┘  └──────┬───────┘  └─────┬──────┘           │  │
│   │       │               │                │                   │  │
│   │  ┌────▼───────────────▼────────────────▼──────┐           │  │
│   │  │        base.py (shared helpers)            │           │  │
│   │  │  - resolve_episode_url()                   │           │  │
│   │  │  - navigate_episode()                      │           │  │
│   │  │  - click_server_option()                   │           │  │
│   │  │  - resolve_iframe_chain()                  │           │  │
│   │  └────────────────────────────────────────────┘           │  │
│   └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
┌─────────┐     ┌──────────┐     ┌──────────┐     ┌──────────────┐
│  User   │────▶│  Next.js │────▶│  Flask   │────▶│  Anichin.moe │
│ Browser │     │  (React) │     │  API     │     │  (Source)    │
└─────────┘     └────┬─────┘     └────┬─────┘     └──────┬───────┘
                     │                │                   │
                     │                │                   │
                     │                ▼                   │
                     │          ┌──────────┐              │
                     │          │ Scraper  │              │
                     │          │ Engine   │              │
                     │          └────┬─────┘              │
                     │               │                   │
                     │               ▼                   │
                     │         ┌──────────┐              │
                     │         │ BeautifulSoup│            │
                     │         │ + Parse  │              │
                     │         └────┬─────┘              │
                     │              │                    │
                     │              ▼                    │
                     │        ┌──────────┐              │
                     │        │ JSON     │              │
                     │        │ Response │              │
                     │        └────┬─────┘              │
                     │             │                    │
                     ▼             ▼                    │
              ┌──────────┐   ┌──────────────┐          │
              │ UI Render │   │ Video Player │          │
              │ (React)  │   │ (iframe)     │          │
              └──────────┘   └──────────────┘          │
                                                       │
              ┌────────────────────────────────────────┘
              │  /api/stream POST
              │  { url, server }
              ▼
      ┌──────────────────┐
      │  Playwright      │
      │  Headless Chrome │
      │  → Click Server  │
      │  → Navigate Chain│
      │  → Extract URL   │
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │  { server,       │
      │    video_url,    │
      │    embed_ready } │
      └──────────────────┘
```

---

## 📦 Instalasi

### Prasyarat

- **Python** 3.11+
- **Node.js** 18+
- **Git**

### 1️⃣ Clone Repository

```bash
git clone https://github.com/VexalynDeveloper/Donglyn.git
cd Donglyn
```

### 2️⃣ Install Backend Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3️⃣ Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 4️⃣ Setup Environment Variables

```bash
cp .env.example .env
```

Edit `.env` dan isi dengan kredensial kamu:

```env
# Flask
SECRET_KEY=your-secret-key-here

# Supabase (opsional, fallback SQLite jika kosong)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email OTP
RESEND_API_KEY=re-your-resend-key
RESEND_FROM_EMAIL=noreply@yourdomain.com

# WhatsApp OTP (Fonnte)
FONNTE_TOKEN=your-fonnte-token

# Dev Panel
DEV_SECRET_KEY=your-dev-secret-key
DEV_PANEL_ADMINS=admin,vexora
```

---

## 🚀 Menjalankan

### Development (Local)

Jalankan Flask API + Next.js bersamaan:

```bash
python run.py
```

Atau jalankan terpisah:

```bash
# Terminal 1 — Flask API
cd backend && python app.py

# Terminal 2 — Next.js
cd frontend && npm run dev
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:5000 |
| Health Check | http://localhost:5000/api/health |

### Production Build

```bash
# Build frontend
cd frontend && npm run build

# Run with gunicorn
cd .. && gunicorn backend.app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

---

## 📂 Struktur Project

```
Donglyn/
│
├── frontend/                          ← Next.js 14 Application
│   ├── app/                           ← App Router pages
│   │   ├── layout.tsx                 ← Root layout (fonts, SEO, head)
│   │   ├── page.tsx                   ← Home (/)
│   │   ├── not-found.tsx              ← 404 page
│   │   │
│   │   ├── search/                    ← Search page
│   │   │   ├── page.tsx
│   │   │   └── SearchContent.tsx
│   │   │
│   │   ├── detail/                    ← Donghua detail page
│   │   │   ├── page.tsx
│   │   │   ├── layout.tsx
│   │   │   └── DetailContent.tsx
│   │   │
│   │   ├── player/                    ← Video player page
│   │   │   ├── page.tsx
│   │   │   └── PlayerContent.tsx
│   │   │
│   │   ├── login/                     ← Login page
│   │   │   └── page.tsx
│   │   ├── register/                  ← Register page
│   │   │   └── page.tsx
│   │   ├── forgot-password/           ← Forgot password
│   │   │   └── page.tsx
│   │   ├── reset-password/            ← Reset password
│   │   │   ├── page.tsx
│   │   │   └── ResetPasswordContent.tsx
│   │   ├── verify-email/              ← Email verification
│   │   │   ├── page.tsx
│   │   │   └── VerifyEmailContent.tsx
│   │   ├── verify-email-sent/         ← Email sent confirmation
│   │   │   └── page.tsx
│   │   │
│   │   ├── profile/                   ← User profile
│   │   │   └── page.tsx
│   │   ├── bookmark/                  ← Bookmarks list
│   │   │   └── page.tsx
│   │   ├── riwayat/                   ← Watch history
│   │   │   └── page.tsx
│   │   ├── genre/                     ← Genre browser
│   │   │   └── page.tsx
│   │   ├── schedule/                  ← Release schedule
│   │   │   └── page.tsx
│   │   ├── terbaru/                   ← Latest episodes
│   │   │   └── page.tsx
│   │   └── dev-panel/                 ← Developer dashboard
│   │       ├── page.tsx
│   │       └── layout.tsx
│   │
│   ├── components/                    ← Reusable components
│   │   ├── layout/
│   │   │   ├── Navbar.tsx             ← Responsive navbar + mobile menu
│   │   │   ├── Footer.tsx             ← Footer with social links
│   │   │   ├── LoadingScreen.tsx      ← Splash screen animation
│   │   │   └── DevPanel.tsx           ← Dev panel modal
│   │   │
│   │   ├── content/
│   │   │   ├── HeroBanner.tsx         ← Swiper hero banner
│   │   │   ├── ContentSection.tsx     ← Content section wrapper
│   │   │   └── PosterCard.tsx         ← Poster card component
│   │   │
│   │   └── ui/
│   │       └── States.tsx             ← Skeleton, EmptyState, ErrorState
│   │
│   ├── lib/                           ← Utilities
│   │   ├── api.ts                     ← API client (fetch wrapper)
│   │   └── types.ts                   ← TypeScript interfaces
│   │
│   ├── hooks/                         ← Custom React hooks
│   │
│   ├── public/                        ← Static assets
│   │   ├── logo.png                   ← Donglyn logo
│   │   ├── favicon.png                ← Favicon
│   │   └── dev-logo.png               ← Dev panel logo
│   │
│   ├── tailwind.config.js             ← Tailwind configuration
│   ├── tsconfig.json                  ← TypeScript configuration
│   ├── postcss.config.js              ← PostCSS configuration
│   ├── eslint.config.mjs              ← ESLint configuration
│   ├── next-env.d.ts                  ← Next.js type declarations
│   ├── package.json                   ← NPM dependencies
│   └── README.md                      ← Frontend documentation
│
├── backend/                           ← Flask API Application
│   ├── app.py                         ← Main Flask app (routes + handlers)
│   │
│   ├── core/                          ← Core utilities
│   │   ├── __init__.py
│   │   └── browser.py                 ← Playwright browser helper
│   │
│   ├── video_engine/                  ← Video streaming engine
│   │   ├── __init__.py
│   │   └── adapters/
│   │       ├── __init__.py
│   │       ├── base.py                ← Shared helpers (navigate, click, chain)
│   │       ├── okru.py                ← Okru server adapter
│   │       ├── dailymotion.py         ← Dailymotion server adapter
│   │       ├── streamwish.py          ← StreamWish server adapter
│   │       ├── flickr.py              ← Flickr server adapter
│   │       └── shortlink.py           ← Shortlink bypass adapter
│   │
│   ├── home.py                        ← Homepage scraper
│   ├── banner.py                      ← Banner slider scraper
│   ├── detail.py                      ← Detail page scraper
│   ├── search.py                      ← Search scraper
│   ├── schedule.py                    ← Schedule scraper
│   ├── genre.py                       ← Genre scraper
│   └── stream.py                      ← Episode URL resolver
│
├── db/                                ← Database setup
│   └── setup_supabase.sql             ← Supabase schema
│
├── .env.example                       ← Environment variables template
├── .gitignore                         ← Git ignore rules
├── AGENTS.md                          ← Agent instructions
├── README.md                          ← This file
├── redesign.md                        ← Master design prompt
├── render.yaml                        ← Render.com deployment config
├── requirements.txt                   ← Python dependencies
└── run.py                             ← Local dev runner
```

---

## 🔌 API Endpoints

### Health

| Method | Endpoint | Response |
|--------|----------|----------|
| GET | `/api/health` | `{"status": "ok"}` |

### Content

| Method | Endpoint | Request Body | Deskripsi |
|--------|----------|--------------|-----------|
| GET | `/api/home` | — | Homepage sections data |
| GET | `/api/banner` | — | Banner slider data |
| GET | `/api/schedule?day=all` | — | Release schedule |
| GET | `/api/genres` | — | Genre list |
| POST | `/api/search` | `{ "q": "string" }` | Search donghua |
| POST | `/api/detail-data` | `{ "url": "string" }` | Detail + episodes |
| POST | `/api/stream` | `{ "url": "string", "server": "Okru" }` | Resolve video URL |

### Proxy

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/proxy-okru` | Proxy Okru video page |
| GET | `/api/proxy-dm` | Proxy Dailymotion page |
| GET | `/api/proxy?url=...` | Generic proxy (CORS-enabled) |

### Auth (Legacy)

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/auth/register` | Register new account |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/send-otp` | Send WhatsApp OTP |
| POST | `/api/auth/verify-phone` | Verify phone OTP |
| POST | `/api/auth/forgot-password` | Send reset link |
| POST | `/api/auth/reset-password` | Reset password |
| POST | `/api/auth/update-profile` | Update profile |
| POST | `/api/auth/upload-avatar` | Upload avatar |

### Bookmarks & History

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/bookmarks` | Get bookmarks |
| POST | `/api/bookmarks` | Add bookmark |
| DELETE | `/api/bookmarks` | Remove bookmark |
| GET | `/api/history` | Get watch history |
| POST | `/api/history` | Add history entry |
| DELETE | `/api/history` | Clear history |

---

## ⚙️ Konfigurasi

### Environment Variables

Lihat `.env.example` untuk daftar lengkap. Yang wajib diisi:

| Variable | Wajib | Deskripsi |
|----------|-------|-----------|
| `SECRET_KEY` | ✅ | Flask session secret |
| `SUPABASE_URL` | ❌ | Supabase project URL |
| `SUPABASE_KEY` | ❌ | Supabase anon key |
| `GOOGLE_CLIENT_ID` | ❌ | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | ❌ | Google OAuth client secret |
| `RESEND_API_KEY` | ❌ | Resend email API key |
| `FONNTE_TOKEN` | ❌ | Fonnte WhatsApp API token |

### Tailwind Content Path

Update `frontend/tailwind.config.js` jika menambahkan path baru:

```js
content: [
  "./app/**/*.{js,ts,jsx,tsx,mdx}",
  "./components/**/*.{js,ts,jsx,tsx,mdx}",
  "./public/**/*.js",
],
```

---

## 🎬 Video Streaming

Engine streaming menggunakan Playwright headless browser untuk menelusuri rantai iframe dari halaman episode hingga mendapatkan URL video akhir.

### Alur Streaming

```
1. User klik "Watch Now" → navigasi ke /player?url=...&server=Okru
2. PlayerContent.tsx → API.post('/api/stream', { url, server })
3. Flask receives request → resolve_episode_url_stable() → full URL
4. Playwright navigates episode page → clicks server button
5. Follows iframe chain: episode → /stream/TOKEN → player → ok.ru/dailymotion/etc
6. Returns JSON: { server, video_url, embed_ready, elapsed_time }
7. Player renders iframe dengan proxy URL
```

### Server yang Didukung

| Server | Status | Proxy |
|--------|--------|-------|
| Okru | ✅ | `/api/proxy-okru` |
| Dailymotion | ✅ | `/api/proxy-dm` |
| StreamWish | ✅ | `/api/proxy` |
| Flickr | ✅ | `/api/proxy` |

---

## 📊 Deployment

### Render.com (Dual Service)

Project dikonfigurasi untuk deploy di Render dengan 2 service:

| Service | Runtime | Build Command | Start Command |
|---------|---------|---------------|---------------|
| `donglyn-api` | Python | `pip install -r requirements.txt` | `gunicorn backend.app:app --bind 0.0.0.0:$PORT` |
| `donglyn-web` | Node.js | `cd frontend && npm ci && npm run build` | `cd frontend && npm start` |

### Local Development

```bash
# Jalankan kedua service sekaligus
python run.py

# Atau terpisah
python -m flask run --port 5000   # Backend
cd frontend && npm run dev        # Frontend
```

---

## 👨‍💻 Developer

| Role | Nama |
|------|------|
| **Project Lead** | Vio Atmajaya Saputra |
| **Backend Engineer** | Vexalyn Developer |
| **Frontend Engineer** | Vexalyn Developer |
| **UI/UX Designer** | Vexalyn Developer |

### Social

[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/VexalynDeveloper)
[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://instagram.com/vexalyn)
[![TikTok](https://img.shields.io/badge/TikTok-000000?style=for-the-badge&logo=tiktok&logoColor=white)](https://tiktok.com/@vexalyn)

---

## 🤝 Contributing

Contributions sangat dipersilakan!

1. **Fork** repository ini
2. **Clone** fork kamu: `git clone https://github.com/username/Donglyn.git`
3. **Create branch**: `git checkout -b fitur/nama-fitur`
4. **Commit** perubahan: `git commit -m 'Add: deskripsi fitur'`
5. **Push** ke branch: `git push origin fitur/nama-fitur`
6. **Buka Pull Request**

### Development Guidelines

- Ikuti **AGENTS.md** untuk instruksi agent
- Gunakan **ESLint** + **Prettier** untuk code style
- Pastikan **build clean** sebelum submit PR
- Update **documentation** jika ada perubahan API

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) untuk detail.

```
MIT License

Copyright (c) 2026 Vexalyn Developer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">

**Dibuat dengan ❤️ oleh [Vexalyn Developer](https://github.com/VexalynDeveloper)**

⭐ Star repo ini jika kamu suka Donglyn!

</div>
