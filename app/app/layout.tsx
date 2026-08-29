import type { Metadata } from "next";
import { Inter, Bebas_Neue } from "next/font/google";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import LoadingScreen from "@/components/layout/LoadingScreen";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const bebas = Bebas_Neue({
  subsets: ["latin"],
  weight: "400",
  variable: "--font-display",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Donglyn — Pusat Streaming Donghua Terlengkap",
    template: "%s | Donglyn",
  },
  description:
    "Nonton donghua terbaru, terlengkap, dan berkualitas. Streaming gratis dengan subtitle Indonesia.",
  keywords: ["donghua", "streaming", "anime", "china", "sub Indo"],
  authors: [{ name: "Vexalyn Developer" }],
  openGraph: {
    type: "website",
    locale: "id_ID",
    siteName: "Donglyn",
    title: "Donglyn — Pusat Streaming Donghua Terlengkap",
    description: "Nonton donghua terbaru dengan subtitle Indonesia.",
  },
  twitter: {
    card: "summary_large_image",
    site: "@donglyn",
    creator: "@donglyn",
  },
  robots: "index, follow",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="id"
      className={`${inter.variable} ${bebas.variable} dark antialiased`}
    >
      <head>
        <link rel="preconnect" href="https://unpkg.com" />
        <link rel="stylesheet" href="https://unpkg.com/lucide@latest" crossOrigin="anonymous" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/brands.min.css" />
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
        <link rel="stylesheet" href="/css/output.css" />
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <style>{`
[data-lucide]{transition:transform .35s cubic-bezier(.34,1.56,.64,1),opacity .25s ease,filter .25s ease;transform-origin:center;will-change:transform}[data-lucide]:hover{transform:scale(1.18);filter:drop-shadow(0 0 6px currentColor)}.icon-bounce[data-lucide]:hover{animation:iconBounce .5s cubic-bezier(.36,.07,.19,.97)}.icon-pulse[data-lucide]:hover{animation:iconPulse .6s ease-in-out infinite alternate}.icon-spin-hover[data-lucide]:hover{animation:iconSpin .6s cubic-bezier(.34,1.56,.64,1)}.icon-shimmer[data-lucide]:hover{animation:iconShimmer .8s ease-in-out}.icon-swing[data-lucide]:hover{animation:iconSwing .5s ease}@keyframes iconBounce{0%,100%{transform:scale(1.18)}40%{transform:scale(1.32)}70%{transform:scale(1.08)}}@keyframes iconPulse{from{transform:scale(1.1);opacity:1}to{transform:scale(1.25);opacity:.8}}@keyframes iconSpin{from{transform:scale(1)rotate(0deg)}to{transform:scale(1.2)rotate(12deg)}}@keyframes iconShimmer{0%{filter:drop-shadow(0 0 2px currentColor) brightness(1)}50%{filter:drop-shadow(0 0 12px currentColor) brightness(1.4)}100%{filter:drop-shadow(0 0 2px currentColor) brightness(1)}}@keyframes iconSwing{0%,100%{transform:scale(1.18)rotate(0deg)}25%{transform:scale(1.18)rotate(-6deg)}75%{transform:scale(1.18)rotate(6deg)}}
.swiper-pagination-bullet{width:16px;height:4px;background:rgba(255,255,255,.42);opacity:1;border-radius:999px;transition:width .35s ease,background .35s ease,transform .35s ease,box-shadow .35s ease}.swiper-pagination-bullet-active{width:28px;background:#E50914;transform:none;box-shadow:0 0 9px rgba(229,9,20,.45)}.swiper-pagination{right:1.5rem !important;left:auto !important;bottom:1.5rem !important;width:auto !important;display:flex;align-items:center;gap:5px;justify-content:flex-end}@media(max-width:767px){.swiper-pagination{display:none !important}}
.nav-wrap{position:relative}.nav-indicator{position:absolute;bottom:-2px;height:2px;background:#e50914;border-radius:2px;transition:left .35s cubic-bezier(.4,0,.2,1),width .35s cubic-bezier(.4,0,.2,1);box-shadow:0 0 10px rgba(229,9,20,.7),0 0 20px rgba(229,9,20,.3);pointer-events:none;opacity:0}.nav-indicator.active{opacity:1}
.desktop-search{position:relative;align-items:center;width:310px;height:42px;padding:4px;background:rgba(25,25,25,.92);border:1px solid rgba(255,255,255,.12);border-radius:999px;box-shadow:0 8px 24px rgba(0,0,0,.2),inset 0 1px 0 rgba(255,255,255,.04);transition:width .3s ease,border-color .25s ease,box-shadow .25s ease}@media(min-width:768px){.desktop-search{display:flex}}.desktop-search:focus-within{width:380px;border-color:rgba(229,9,20,.65);box-shadow:0 0 0 3px rgba(229,9,20,.12),0 10px 28px rgba(0,0,0,.28),inset 0 1px 0 rgba(255,255,255,.05)}.desktop-search-icon{width:34px;flex:none;text-align:center;color:rgba(255,255,255,.48);transition:color .25s ease}.desktop-search:focus-within .desktop-search-icon{color:#e50914}.desktop-search-input{min-width:0;flex:1;height:32px;padding:0 8px;color:#fff;background:transparent;border:0;outline:0;font-size:13px;font-weight:500}.desktop-search-input::placeholder{color:rgba(255,255,255,.38)}.desktop-search-key{flex:none;margin-right:7px;padding:3px 6px;color:rgba(255,255,255,.35);border:1px solid rgba(255,255,255,.12);border-radius:5px;font:600 10px/1 Inter,sans-serif;transition:opacity .2s ease}.desktop-search:focus-within .desktop-search-key{opacity:0;pointer-events:none}.desktop-search-button{display:flex;align-items:center;justify-content:center;gap:6px;flex:none;height:32px;padding:0 13px;border:0;border-radius:999px;background:#e50914;color:#fff;font-size:11px;font-weight:900;letter-spacing:.02em;cursor:pointer;transition:background .2s ease,transform .2s ease}.desktop-search-button:hover{background:#f40612;transform:translateY(-1px)}.desktop-search-button:active{transform:translateY(0)}
.auth-nav-button{height:32px;align-items:center;justify-content:center;line-height:1;border-radius:999px;padding:0 13px;background:#e50914;border:none;font-size:11px;font-weight:900;letter-spacing:.02em;transition:background .2s ease,transform .15s ease,box-shadow .2s ease;box-shadow:0 2px 12px rgba(229,9,20,.35);margin-left:0;position:relative;z-index:1;cursor:pointer}.auth-nav-button:hover{background:#b20710;transform:translateY(-1px);box-shadow:inset -2px 0 0 rgba(0,0,0,.15),0 4px 20px rgba(229,9,20,.5)}.auth-nav-button:active{transform:translateY(0)}@media(max-width:767px){.auth-nav-button{display:none !important}}
.guest-profile-icon{display:flex;align-items:center;justify-content:center;width:34px;height:34px;border:1px solid rgba(229,9,20,.35);border-radius:50%;background:rgba(229,9,20,.1);color:#e50914;font-size:15px;transition:transform .25s ease,background .25s ease,box-shadow .25s ease}.guest-profile-icon.hidden{display:none}#userMenu:hover .guest-profile-icon{transform:translateY(-1px);background:rgba(229,9,20,.18);box-shadow:0 0 0 4px rgba(229,9,20,.08),0 8px 18px rgba(0,0,0,.25)}
.guest-auth-card{padding:14px 16px 12px;border-bottom:1px solid rgba(255,255,255,.1)}.guest-auth-kicker{margin-bottom:3px;color:rgba(255,255,255,.42);font-size:10px;font-weight:800;letter-spacing:.12em;text-transform:uppercase}.guest-auth-title{color:#fff;font-size:14px;font-weight:800}
.user-auth-panel{display:flex;align-items:center;gap:12px;padding:14px 16px;border-bottom:1px solid rgba(255,255,255,.1)}.user-auth-panel.hidden{display:none}
.user-dropdown{opacity:0;transform:translateY(-8px) scale(.97);pointer-events:none;transition:opacity .2s ease,transform .2s cubic-bezier(.4,0,.2,1)}.user-dropdown.open{opacity:1;transform:translateY(0) scale(1);pointer-events:auto}.user-dropdown.closing{opacity:0;transform:translateY(-8px) scale(.97);pointer-events:none}
.hamburger-line{transform-origin:center}#mobileMenuBtn.open .hamburger-line:nth-child(1){transform:translateY(7px) rotate(45deg);background:#e50914}#mobileMenuBtn.open .hamburger-line:nth-child(2){opacity:0;transform:scaleX(0)}#mobileMenuBtn.open .hamburger-line:nth-child(3){transform:translateY(-7px) rotate(-45deg);background:#e50914}
.scrollbar-hide{-ms-overflow-style:none;scrollbar-width:none}.scrollbar-hide::-webkit-scrollbar{display:none}
`}</style>
      <body className="min-h-screen bg-[#050505] text-[#f5f5f5] font-sans selection:bg-[#e50914] selection:text-white">
        <LoadingScreen />
        <Navbar />
        <main className="pt-[72px] min-h-screen">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
