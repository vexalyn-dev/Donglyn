"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function PlayerContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const url = searchParams.get("url") || "";
  const title = searchParams.get("title") || "";
  const episode = searchParams.get("episode") || "";
  const server = searchParams.get("server") || "Default";

  useEffect(() => {
    if (!url) router.replace("/");
  }, [url, router]);

  if (!url) return null;

  const iframeUrl = `/stream?url=${encodeURIComponent(url)}&server=${server}`;

  return (
    <div className="max-w-[1600px] mx-auto px-4 md:px-8 py-4">
      <div className="relative aspect-video rounded-xl overflow-hidden bg-black border border-white/10 shadow-2xl">
        <iframe src={iframeUrl} className="absolute inset-0 w-full h-full" allowFullScreen allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" title={`${title} - Episode ${episode}`} />
      </div>
      <div className="mt-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-black text-white">{title}</h1>
          <p className="text-white/50 text-sm mt-1">Episode {episode}</p>
        </div>
        <span className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-white/70 text-sm">Server: {server}</span>
      </div>
      <div className="mt-4 flex gap-3">
        <button onClick={() => router.back()} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 border border-white/20 text-white text-sm font-medium hover:bg-white/15 transition">
          <i data-lucide="arrow-left" className="w-4 h-4" />Kembali
        </button>
      </div>
    </div>
  );
}
