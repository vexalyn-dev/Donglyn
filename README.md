# VEXORA

Platform Streaming Donghua Gratis — Netflix Style

[![GitHub stars](https://img.shields.io/github/stars/VexalynDeveloper/VEXORA?style=flat-square&color=e50914)](https://github.com/VexalynDeveloper/VEXORA)
[![GitHub forks](https://img.shields.io/github/forks/VexalynDeveloper/VEXORA?style=flat-square&color=ff6b35)](https://github.com/VexalynDeveloper/VEXORA)
[![GitHub issues](https://img.shields.io/github/issues/VexalynDeveloper/VEXORA?style=flat-square&color=f5a623)](https://github.com/VexalynDeveloper/VEXORA/issues)
[![GitHub watchers](https://img.shields.io/github/watchers/VexalynDeveloper/VEXORA?style=flat-square&color=4a90d9)](https://github.com/VexalynDeveloper/VEXORA)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-3.0+-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Tailwind CSS](https://img.shields.io/badge/tailwindcss-3.4+-06b6d4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![Playwright](https://img.shields.io/badge/playwright-1.40+-2ead33?style=flat-square&logo=playwright&logoColor=white)](https://playwright.dev)
[![Supabase](https://img.shields.io/badge/supabase-Powered-3ecf8e?style=flat-square&logo=supabase&logoColor=white)](https://supabase.com)

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Inter&weight=700&size=18&duration=3000&pause=1000&color=F7F7F7&center=true&vCenter=true&multiline=true&repeat=true&width=600&height=80&lines=%F0%9F%8E%AC+Nonton+Donghua+Gratis+Kualitas+HD%3B%F0%9F%94%84+Real-Time+Update+ dari+Anichin.moe%3B%F0%9F%A7%A0+Netflix+Style+UI+%2B+Dark+Mode)](https://github.com/VexalynDeveloper/VEXORA)

---

## Daftar Isi

- [Tentang VEXORA](#tentang-vexora)
- [Fitur](#fitur)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Cara Instalasi](#cara-instalasi)
- [Cara Menjalankan](#cara-menjalankan)
- [Konfigurasi](#konfigurasi)
- [Struktur Project](#struktur-project)
- [API Endpoints](#api-endpoints)
- [Screenshot](#screenshot)
- [Contributing](#contributing)
- [Author](#author)
- [License](#license)

---

## Tentang VEXORA

VEXORA adalah platform streaming donghua (animasi China) gratis dengan tampilan ala Netflix. Website ini scrape data dari [anichin.moe](https://anichin.moe) secara real-time menggunakan Playwright untuk bypass Cloudflare, lalu ditampilkan dengan UI yang modern, responsive, dan user-friendly.

### Kenapa VEXORA?

- 🎬 Tampilan Netflix-style yang premium
- 🌙 Dark mode full — nyaman di mata
- 📱 Responsive — work di HP, tablet, dan desktop
- ⚡ Fast loading dengan lazy loading & caching
- 🔐 Auth lengkap — email, Google OAuth, WhatsApp OTP
- 🌍 Multi-language — Indonesia, English, Japanese, Chinese

---

## Fitur

| Fitur | Status | Deskripsi |
| --- | --- | --- |
| 🎬 Banner Slider | ✅ | Swiper.js dengan efek creative, auto-slide 3 detik |
| 🔍 Real-Time Search | ✅ | Pencarian langsung dari anichin.moe, hasil muncul di halaman |
| 📂 Genre Filter | ✅ | Filter berdasarkan genre donghua |
| 📅 Schedule | ✅ | Jadwal rilis donghua |
| 📑 Bookmark | ✅ | Simpan donghua favorit (localStorage + Supabase) |
| 📖 Riwayat | ✅ | Histori tontonan otomatis |
| 🔐 Login/Register | ✅ | Email + password, Google OAuth, WhatsApp OTP |
| 📧 Lupa Password | ✅ | Reset via email (Resend API) atau WhatsApp (Fonnte) |
| 🎭 Profil | ✅ | Ganti avatar, username, email |
| 🌍 Multi-language | ✅ | Indonesia, English, Japanese, Chinese |
| 📱 Responsive | ✅ | Mobile-first, hamburger menu |
| ⚡ Lazy Loading | ✅ | Gambar load saat dibutuhkan |
| 🔗 Proxy Player | ✅ | Bypass CORS untuk video player |
| 🌙 Dark Mode | ✅ | Full dark theme Netflix-style |

---

## Tech Stack

### Frontend

| Teknologi | Versi | Fungsi |
| --- | --- | --- |
| HTML5 | - | Struktur halaman |
| Tailwind CSS | 3.4+ | Utility-first CSS framework |
| JavaScript | ES6+ | Interaktivitas & AJAX |
| Swiper.js | 11.x | Banner slider |
| Font Awesome | 6.5+ | Icons |
| Google Fonts | - | Bebas Neue + Inter |

### Backend

| Teknologi | Versi | Fungsi |
| --- | --- | --- |
| Python | 3.11+ | Bahasa utama |
| Flask | 3.0+ | Web framework |
| SQLite | - | Database lokal (fallback) |
| Supabase | - | Database cloud (users, bookmarks, history) |
| Playwright | 1.40+ | Web scraping (Cloudflare bypass) |
| BeautifulSoup4 | - | HTML parsing |
| Resend | - | Email OTP |
| Fonnte API | - | WhatsApp OTP |
| Google Auth | - | OAuth 2.0 |

### Scraping

| Tool | Fungsi |
| --- | --- |
| Playwright (async) | Buka anichin.moe via headless Chromium, bypass Cloudflare |
| BeautifulSoup4 | Parse HTML hasil scrape, extract data donghua |
| Requests | HTTP fallback kalau Playwright gagal |

---

## System Architecture

```text
┌──────────────────────────────────────────────────────────┐
│                      CLIENT (Browser)                    │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  HTML   │  │ Tailwind │  │    JS    │  │ Swiper.js│ │
│  │ Template│  │   CSS    │  │ AJAX +   │  │  Slider  │ │
│  │  (Jinja)│  │          │  │ Fetch API│  │          │ │
│  └────┬────┘  └────┬─────┘  └────┬─────┘  └──────────┘ │
└───────┼────────────┼─────────────┼──────────────────────┘
        │            │             │
        ▼            ▼             ▼
┌──────────────────────────────────────────────────────────┐
│                    FLASK BACKEND (app.py)                 │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │   Auth   │  │  Search  │  │  Banner  │  │  Proxy  │ │
│  │ Register │  │ /api/    │  │ /api/    │  │ /api/   │ │
│  │ Login    │  │ search   │  │ banner   │  │ proxy-  │ │
│  │ Google   │  │          │  │          │  │ player  │ │
│  │ OTP      │  │          │  │          │  │         │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘ │
└───────┼──────────────┼─────────────┼──────────────┼──────┘
        │              │             │              │
        ▼              ▼             ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Supabase │   │Playwright│   │ Anichin  │   │ Anichin  │
│ (Cloud)  │   │ Headless │   │   .moe   │   │  Player  │
│          │   │ Chromium │   │ (Source) │   │  (Video) │
│ users    │   │          │   │          │   │          │
│ bookmarks│   │ Scrape + │   │ Banner + │   │ Stream   │
│ history  │   │ Parse    │   │ Content  │   │ URL      │
└──────────┘   └──────────┘   └──────────┘   └──────────┘
```

### Data Flow

```text
User Request → Flask Router → Handler Function
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              Auth Check      Scraping API      Static Files
              (Supabase/      (Playwright/      (Tailwind/
               SQLite)         Requests)         Assets)
                    │               │               │
                    ▼               ▼               ▼
              Session/         HTML Parse      CSS/JS/Img
              JWT Token       (BeautifulSoup)   Response
```

---

## Cara Instalasi

### Prasyarat

- Python 3.11 atau lebih tinggi
- Node.js (untuk compile Tailwind CSS)
- Git

### 1. Clone Repository

```bash
git clone https://github.com/VexalynDeveloper/VEXORA.git
cd VEXORA
```

### 2. Install Dependencies Python

```bash
pip install -r requirements.txt
```

Atau install manual:

```bash
pip install flask playwright beautifulsoup4 requests python-dotenv
pip install google-auth supabase resend werkzeug
```

### 3. Install Playwright Browser

```bash
playwright install chromium
```

### 4. Install Node.js Dependencies (untuk Tailwind)

```bash
npm install -D tailwindcss
```

### 5. Setup Environment Variables

Copy `.env.example` ke `.env`:

```bash
copy .env.example .env
```

Lalu isi `.env` dengan credentials kamu (lihat bagian [Konfigurasi](#konfigurasi)).

### 6. Setup Supabase (Opsional)

Kalau mau pakai Supabase cloud:

1. Buat akun di [supabase.com](https://supabase.com)
2. Buat project baru
3. Buka SQL Editor
4. Jalankan isi `setup_supabase.sql`
5. Copy URL dan API Key ke `.env`

---

## Cara Menjalankan

### 1. Compile Tailwind CSS

```bash
npx tailwindcss -i ./static/src/input.css -o ./static/css/output.css --minify
```

### 2. Jalankan Server

```bash
python app.py
```

### 3. Buka Browser

```text
http://127.0.0.1:5000
```

---

## Konfigurasi

Buka file `.env` dan isi:

```env
# Google OAuth 2.0 (daftar di console.cloud.google.com)
GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxxx

# Fonnte WhatsApp API (gratis 1000 msg/bulan di md.fonnte.com)
FONNTE_TOKEN=xxxxx

# Resend Email API (gratis 100 emails/hari di resend.com)
RESEND_API_KEY=re_xxxxx
RESEND_FROM_EMAIL=noreply@domainkamu.com

# Supabase (gratis di supabase.com → Settings → API)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJxxxxx

# Flask Secret Key
SECRET_KEY=bebas-isi-random
```

### Penjelasan Tiap API Key

| API Key | Dapat dari | Fungsi | Gratis? |
| --- | --- | --- | --- |
| `GOOGLE_CLIENT_ID` | [Google Cloud Console](https://console.cloud.google.com/apis/credentials) | Login via Google | ✅ |
| `GOOGLE_CLIENT_SECRET` | Google Cloud Console | OAuth secret | ✅ |
| `FONNTE_TOKEN` | [Fonnte](https://md.fonnte.com) | Kirim OTP via WhatsApp | ✅ (1000/bln) |
| `RESEND_API_KEY` | [Resend](https://resend.com/api-keys) | Kirim OTP via Email | ✅ (100/hari) |
| `SUPABASE_KEY` | [Supabase Dashboard](https://supabase.com/dashboard) → Settings → API | Database cloud | ✅ (500MB) |

---

## Struktur Project

```text
VEXORA/
├── app.py                  # Main Flask application (routes, scraping, auth)
├── search.py               # Standalone search scraper (reference)
├── banner.py               # Banner scraper (reference)
├── setup_supabase.sql      # SQL setup untuk Supabase
├── .env                    # Environment variables (JANGAN commit!)
├── .gitignore              # Git ignore rules
├── users.db                # SQLite database (auto-created)
│
├── core/
│   └── browser.py          # Playwright browser helper
│
├── static/
│   ├── src/
│   │   └── input.css       # Tailwind source CSS
│   ├── css/
│   │   └── output.css      # Compiled Tailwind CSS (minified)
│   ├── uploads/            # User uploaded avatars
│   └── favicon.svg         # Favicon (huruf V merah)
│
├── asset/
│   ├── logo.png            # VEXORA logo
│   ├── dev-logo.png        # Developer logo
│   └── bg-login & register.png  # Background login page
│
└── templates/
    ├── index.html          # Home page (banner, search, sections)
    ├── login.html          # Login page (Netflix-style)
    ├── register.html       # Register page (Netflix-style)
    ├── forgot.html         # Forgot password (4 steps)
    ├── detail.html         # Anime detail page
    ├── player.html         # Video player page
    ├── genre.html          # Genre filter page
    ├── schedule.html       # Schedule page
    ├── bookmark.html       # Bookmark page
    ├── riwayat.html        # History page
    ├── profile.html        # User profile page
    └── section.html        # Section detail page
```

---

## API Endpoints

### Auth

| Method | Endpoint | Fungsi |
| --- | --- | --- |
| POST | `/api/auth/register` | Register akun baru |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/google` | Login/Register via Google |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Cek status login |
| POST | `/api/auth/send-otp` | Kirim OTP WhatsApp |
| POST | `/api/auth/verify-phone` | Verifikasi OTP phone |
| POST | `/api/auth/forgot-password` | Kirim OTP reset password |
| POST | `/api/auth/verify-reset-otp` | Verifikasi OTP reset |
| POST | `/api/auth/reset-password` | Reset password |
| POST | `/api/auth/update-profile` | Update username/email |
| POST | `/api/auth/upload-avatar` | Upload avatar |

### Content

| Method | Endpoint | Fungsi |
| --- | --- | --- |
| GET | `/api/home` | Data home (sections) |
| GET | `/api/banner` | Banner slider data |
| GET | `/api/search?q=...` | Pencarian donghua |
| GET | `/api/genre` | Daftar genre |
| GET | `/api/genre/<slug>` | Donghua per genre |
| GET | `/api/schedule` | Jadwal rilis |
| GET | `/api/detail-data?url=...` | Detail donghua |
| GET | `/api/proxy-player?url=...` | Proxy video player |

### Data

| Method | Endpoint | Fungsi |
| --- | --- | --- |
| GET | `/api/bookmarks` | Ambil bookmarks |
| POST | `/api/bookmarks` | Tambah bookmark |
| DELETE | `/api/bookmarks` | Hapus bookmark |
| GET | `/api/history` | Ambil riwayat |
| POST | `/api/history` | Tambah/update riwayat |
| DELETE | `/api/history` | Hapus riwayat |

---

## Screenshot

| Home | Detail | Player |
| --- | --- | --- |
| ![Home](screenshot-home.png) | ![Detail](screenshot-detail.png) | ![Player](screenshot-player.png) |

| Login | Mobile | Search |
| --- | --- | --- |
| ![Login](screenshot-login.png) | ![Mobile](screenshot-mobile.png) | ![Search](screenshot-search.png) |

---

## Contributing

Contributions sangat dipersilakan! Kalau kamu mau:

1. Fork repository ini
2. Buat branch baru (`git checkout -b fitur/xxx`)
3. Commit perubahan (`git commit -m 'Add fitur xxx'`)
4. Push ke branch (`git push origin fitur/xxx`)
5. Buka Pull Request

### Bug Report

Kalau nemu bug, buka [GitHub Issues](https://github.com/VexalynDeveloper/VEXORA/issues) dan kasih:

- Deskripsi bug
- Screenshot/video
- Console log (kalau ada error)

---

## Author

Vexalyn Developer

Vio Atmajaya Saputra

[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://instagram.com/vexalyn)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/VexalynDeveloper)
[![TikTok](https://img.shields.io/badge/TikTok-000000?style=for-the-badge&logo=tiktok&logoColor=white)](https://tiktok.com/@vexalyn)

Dibuat dengan ❤️ untuk komunitas donghua Indonesia

---

## License

```text
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

⭐ Star repo ini kalau kamu suka VEXORA! ⭐

Made with Python & ❤️ by [Vexalyn Developer](https://github.com/VexalynDeveloper)
