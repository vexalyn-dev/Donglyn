"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import type { DetailData } from "@/lib/types";

export default function DetailContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const url = searchParams.get("url") || "";
  const [data, setData] = useState<DetailData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedEpisode, setSelectedEpisode] = useState<number>(0);
  const [selectedServer, setSelectedServer] = useState("Default");
  const [bookmarked, setBookmarked] = useState(false);

  useEffect(() => {
    if (!url) {
      router.replace("/");
      return;
    }
    setLoading(true);
    api.getDetail(url)
      .then((res) => setData(res))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [url, router]);

  const handleWatch = () => {
    if (!data?.episodes?.[selectedEpisode]) return;
    const episode = data.episodes[selectedEpisode];
    router.push(`/player?url=${encodeURIComponent(episode.url)}&server=${selectedServer}&title=${encodeURIComponent(data.title)}&episode=${encodeURIComponent(episode.episode || "")}`);
  };

  const handleBookmark = async () => {
    if (!data) return;
    try {
      if (bookmarked) {
        await api.removeBookmark({ donghua_id: data.title });
      } else {
        await api.addBookmark({ donghua_id: data.title, title: data.title, url: url, poster: data.poster });
      }
      setBookmarked(!bookmarked);
    } catch {
      router.push("/login");
    }
  };

  if (loading) {
    return (
      <div className="max-w-[1600px] mx-auto px-4 md:px-8 py-6">
        <div className="animate-pulse">
          <div className="h-96 bg-white/5 rounded-2xl mb-6" />
          <div className="grid grid-cols-[200px_1fr] gap-6">
            <div className="aspect-[2/3] bg-white/5 rounded-xl" />
            <div className="space-y-4">
              <div className="h-8 bg-white/5 rounded w-3/4" />
              <div className="h-4 bg-white/5 rounded w-1/2" />
              <div className="h-20 bg-white/5 rounded" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="max-w-[1600px] mx-auto px-4 md:px-8 py-20 text-center">
        <div className="w-16 h-16 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto mb-4">
          <i data-lucide="alert-circle" className="w-8 h-8 text-red-500" />
        </div>
        <p className="text-white/70 mb-4">Donghua tidak ditemukan</p>
        <button onClick={() => router.back()} className="px-4 py-2 rounded-full bg-white/10 border border-white/20 text-white text-sm hover:bg-white/15 transition">
          Kembali
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-[1600px] mx-auto px-4 md:px-8 py-6">
      {/* Backdrop */}
      <div className="relative h-[40vh] md:h-[50vh] lg:h-[60vh] rounded-2xl overflow-hidden mb-6">
        {data.backdrop ? (
          <img src={data.backdrop} alt={data.title} className="w-full h-full object-cover" loading="eager" decoding="async" />
        ) : (
          <img src={data.poster} alt={data.title} className="w-full h-full object-cover blur-sm scale-110" loading="eager" decoding="async" />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/50 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-r from-background/80 via-transparent to-transparent" />
      </div>

      {/* Content */}
      <div className="relative -mt-[40vh] md:-mt-[50vh] lg:-mt-[55vh] px-4 md:px-8">
        <div className="flex gap-6">
          {/* Poster */}
          <div className="flex-shrink-0">
            <div className="w-[160px] md:w-[200px] rounded-xl overflow-hidden shadow-2xl border border-white/10">
              <img src={data.poster} alt={data.title} className="w-full aspect-[2/3] object-cover" loading="eager" decoding="async" />
            </div>
          </div>

          {/* Info */}
          <div className="flex-1 pt-4 md:pt-8">
            <h1 className="text-2xl md:text-4xl font-black text-white mb-3 leading-tight">{data.title}</h1>
            <div className="flex flex-wrap items-center gap-3 mb-4 text-sm">
              {data.rating && (
                <span className="flex items-center gap-1 text-yellow-500">
                  <i data-lucide="star" className="w-4 h-4 fill-current" />{data.rating}
                </span>
              )}
              {data.year && <span className="text-white/50">{data.year}</span>}
              {data.status && (
                <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-donglyn/20 border border-donglyn/30 text-donglyn text-xs font-bold">
                  <span className={`w-1.5 h-1.5 rounded-full ${data.status === "Ongoing" ? "bg-donglyn animate-pulse" : "bg-white/60"}`} />
                  {data.status}
                </span>
              )}
              {data.episodes && (
                <span className="text-white/50 flex items-center gap-1">
                  <i data-lucide="film" className="w-4 h-4" />{data.episodes.length} Episodes
                </span>
              )}
            </div>

            {data.genres && data.genres.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-5">
                {data.genres.map((g) => (
                  <span key={g} className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-white/70 text-xs font-medium">{g}</span>
                ))}
              </div>
            )}

            {data.description && (
              <p className="text-white/60 text-sm leading-relaxed mb-6 max-w-2xl line-clamp-3">{data.description}</p>
            )}

            <div className="flex flex-wrap gap-3">
              <button onClick={handleWatch} disabled={!data.episodes?.[selectedEpisode]} className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-donglyn text-white font-black text-sm hover:bg-[#f40612] transition-all duration-200 hover:-translate-y-0.5 hover:shadow-[0_8px_24px_rgba(229,9,20,.4)] disabled:opacity-50 disabled:cursor-not-allowed">
                <i data-lucide="play" className="w-4 h-4 fill-current" />MULAI STREAMING
              </button>
              <button onClick={handleBookmark} className={`inline-flex items-center gap-2 px-6 py-3 rounded-full font-black text-sm transition-all duration-200 hover:-translate-y-0.5 ${bookmarked ? "bg-donglyn/20 border border-donglyn/40 text-donglyn" : "bg-white/10 border border-white/20 text-white hover:bg-white/15"}`}>
                <i data-lucide={bookmarked ? "bookmark" : "bookmark-plus"} className="w-4 h-4" />{bookmarked ? "Sudah Di Bookmark" : "Tambah ke Daftar"}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Episodes */}
      {data.episodes && data.episodes.length > 0 && (
        <section className="mt-10">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-xl font-black text-white">Episodes</h2>
            <span className="text-white/40 text-sm">{data.episodes.length} episode</span>
          </div>

          {data.servers && data.servers.length > 1 && (
            <div className="mb-5">
              <p className="text-white/50 text-sm mb-2">Server:</p>
              <div className="flex flex-wrap gap-2">
                {data.servers.map((s) => (
                  <button key={s} onClick={() => setSelectedServer(s)} className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${selectedServer === s ? "bg-donglyn/20 border border-donglyn/40 text-donglyn" : "bg-white/5 border border-white/10 text-white/70 hover:border-white/20 hover:text-white"}`}>{s}</button>
                ))}
              </div>
            </div>
          )}

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
            {data.episodes.map((ep, i) => (
              <button key={i} onClick={() => setSelectedEpisode(i)} className={`px-4 py-3 rounded-lg text-sm font-medium transition-all text-left ${selectedEpisode === i ? "bg-donglyn text-white" : "bg-white/5 border border-white/10 text-white/70 hover:border-white/20 hover:text-white"}`}>
                <div className="font-bold">{ep.episode}</div>
                {ep.title && <div className="text-[10px] text-white/50 truncate mt-0.5">{ep.title}</div>}
              </button>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
