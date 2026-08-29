"use client";

import Link from "next/link";
import { useEffect } from "react";

export default function Footer() {
  useEffect(() => {
    // Re-initialize Lucide icons in footer
    if (typeof window !== "undefined" && (window as any).lucide) {
      (window as any).lucide.createIcons();
    }
  }, []);

  return (
    <footer className="bg-black border-t border-white/10 mt-12">
      <div className="max-w-[1600px] mx-auto px-4 md:px-10 py-10">
        {/* Logo */}
        <div className="mb-5">
          <img
            src="/logo.png"
            alt="Donglyn"
            className="h-7 w-auto object-contain"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = "none";
            }}
          />
        </div>

        {/* Social Icons */}
        <div className="flex gap-3 mb-6">
          <a
            href="#"
            className="w-8 h-8 border border-white/20 rounded-full flex items-center justify-center hover:bg-white hover:text-black transition"
            aria-label="Instagram Donglyn"
            title="Instagram"
          >
            <i className="fa-brands fa-instagram text-sm" />
          </a>
          <a
            href="#"
            className="w-8 h-8 border border-white/20 rounded-full flex items-center justify-center hover:bg-white hover:text-black transition"
            aria-label="TikTok Donglyn"
            title="TikTok"
          >
            <i className="fa-brands fa-tiktok text-sm" />
          </a>
          <a
            href="#"
            className="w-8 h-8 border border-white/20 rounded-full flex items-center justify-center hover:bg-white hover:text-black transition"
            aria-label="Github Donglyn"
            title="Github"
          >
            <i className="fa-brands fa-github text-sm" />
          </a>
        </div>

        {/* Links Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-xs mb-6">
          <div className="space-y-3 text-white/40">
            <a href="#" className="block hover:text-white/80 hover:underline">
              Audio Description
            </a>
            <a href="#" className="block hover:text-white/80">
              Investor Relations
            </a>
            <a href="#" className="block hover:text-white/80">
              Legal Notices
            </a>
            <Link href="/" className="block hover:text-white">
              Beranda
            </Link>
          </div>
          <div className="space-y-3 text-white/40">
            <a href="#" className="block hover:text-white/80">
              Help Center
            </a>
            <a href="#" className="block hover:text-white/80">
              Jobs
            </a>
            <a href="#" className="block hover:text-white/80">
              Cookie Preferences
            </a>
            <Link href="/genre" className="block hover:text-white">
              Genre
            </Link>
          </div>
          <div className="space-y-3 text-white/40">
            <a href="#" className="block hover:text-white/80">
              Gift Cards
            </a>
            <Link href="/terbaru" className="block hover:text-white">
              Terbaru
            </Link>
            <a href="#" className="block hover:text-white/80">
              Terms of Use
            </a>
            <a href="#" className="block hover:text-white/80">
              Corporate Information
            </a>
          </div>
          <div className="space-y-3 text-white/40">
            <a href="#" className="block hover:text-white/80">
              Media Center
            </a>
            <a href="#" className="block hover:text-white/80">
              Privacy
            </a>
            <a href="#" className="block hover:text-white/80">
              Contact Us
            </a>
            <Link href="/bookmark" className="block hover:text-white">
              Bookmark
            </Link>
          </div>
        </div>

        {/* Creator + Copyright */}
        <div className="mt-4 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div>
            <span className="text-[10px] font-black tracking-[0.25em] text-donglyn uppercase">
              CRAFTED BY
            </span>
            <button
              type="button"
              className="mt-0.5 block cursor-pointer rounded-lg border border-white/10 transition hover:border-donglyn/60 hover:shadow-[0_0_18px_rgba(229,9,20,.25)]"
              aria-label="Vexalyn Developer"
              title="Vexalyn Developer"
            >
              <img
                src="/dev-logo.png"
                alt="Vexalyn Developer"
                className="h-6 w-20 object-contain"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = "none";
                }}
              />
            </button>
          </div>
          <p className="text-[11px] text-white/20">
            &copy; 2026 Donglyn &bull; Dibuat oleh Vexalyn Developer{" "}
            <span className="text-donglyn font-bold">[Vio Atmajaya]</span>
          </p>
        </div>
      </div>
    </footer>
  );
}
