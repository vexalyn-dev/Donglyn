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
    default: "Donglyn â€” Pusat Streaming Donghua Terlengkap",
    template: "%s | Donglyn",
  },
  description: "Nonton donghua terbaru, terlengkap, dan berkualitas. Streaming gratis dengan subtitle Indonesia.",
  keywords: ["donghua", "streaming", "anime", "china", "sub Indo"],
  authors: [{ name: "Vexalyn Developer" }],
  openGraph: {
    type: "website",
    locale: "id_ID",
    siteName: "Donglyn",
    title: "Donglyn â€” Pusat Streaming Donghua Terlengkap",
    description: "Nonton donghua terbaru dengan subtitle Indonesia.",
  },
  twitter: { card: "summary_large_image", site: "@donglyn", creator: "@donglyn" },
  robots: "index, follow",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id" className={`${inter.variable} ${bebas.variable} dark antialiased`}>
      <head>
        <link rel="preconnect" href="https://unpkg.com" />
        <link rel="stylesheet" href="https://unpkg.com/lucide@latest" crossOrigin="anonymous" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/brands.min.css" />
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
        <link rel="stylesheet" href="/css/output.css" />
        <link rel="icon" href="/favicon.png" type="image/svg+xml" />
      </head>
      <body className="min-h-screen bg-[#050505] text-[#f5f5f5] font-sans selection:bg-[#e50914] selection:text-white">
        <LoadingScreen />
        <Navbar />
        <main className="pt-[72px] min-h-screen">{children}</main>
        <Footer />
      </body>
    </html>
  );
}


