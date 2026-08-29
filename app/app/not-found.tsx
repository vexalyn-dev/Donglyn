import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "404 - Page Not Found | Donglyn",
  description: "Halaman tidak ditemukan",
};

export default function NotFoundPage() {
  return (
    <div className="min-h-[calc(100vh-72px)] flex items-center justify-center px-4">
      <div className="text-center">
        <h1 className="text-8xl font-black text-donglyn mb-4">404</h1>
        <p className="text-white/70 text-lg mb-2">Halaman tidak ditemukan</p>
        <p className="text-white/40 text-sm mb-8">Maaf, halaman yang kamu cari tidak ada.</p>
        <a
          href="/"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-donglyn text-white font-black text-sm hover:bg-[#f40612] transition-all duration-200 hover:-translate-y-0.5 hover:shadow-[0_8px_24px_rgba(229,9,20,.4)]"
        >
          <i data-lucide="home" className="w-4 h-4" />
          Kembali ke Beranda
        </a>
      </div>
    </div>
  );
}
