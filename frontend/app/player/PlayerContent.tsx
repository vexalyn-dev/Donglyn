"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "@/lib/api";

const SERVERS = ["Okru", "Dailymotion", "StreamWish", "Flickr"];

export default function PlayerContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const url = searchParams.get("url") || "";
  const title = searchParams.get("title") || "";
  const episode = searchParams.get("episode") || "";
  const initialServer = searchParams.get("server") || "Okru";

  const [streamData, setStreamData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentServer, setCurrentServer] = useState(initialServer);
  const [availableServers, setAvailableServers] = useState<string[]>([]);

  const fetchStream = async (server: string) => {
    setLoading(true);
    setError(null);
    setStreamData(null);
    try {
      const res = await api.getStream({ url, server });
      if (res && res.video_url) {
        setStreamData(res);
        setCurrentServer(server);
        setError(null);
      } else {
        throw new Error(res?.error || "Server returned no video URL");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load stream");
      setStreamData(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!url) {
      router.replace("/");
      return;
    }
    fetchStream(currentServer);
  }, [url]);

  const handleServerChange = (srv: string) => {
    setCurrentServer(srv);
    fetchStream(srv);
  };

  if (!url) return null;

  return (
    <div className="max-w-[1600px] mx-auto px-4 md:px-8 py-4">
      {/* Player */}
      <div className="relative aspect-video rounded-xl overflow-hidden bg-black border border-white/10 shadow-2xl">
        {loading ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3">
            <i data-lucide="loader-2" className="w-8 h-8 text-donglyn animate-spin" />
            <p className="text-white/50 text-sm">Memuat server {currentServer}...</p>
          </div>
        ) : error ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-black/80">
            <i data-lucide="alert-circle" className="w-10 h-10 text-red-500" />
            <p className="text-white/70 text-sm text-center px-4">{error}</p>
            <button
              onClick={() => fetchStream(currentServer)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-donglyn/20 border border-donglyn/40 text-donglyn text-sm font-medium hover:bg-donglyn/30 transition"
            >
              <i data-lucide="refresh-cw" className="w-4 h-4" />Coba Lagi
            </button>
          </div>
        ) : streamData?.iframe_url ? (
          <iframe
            src={streamData.iframe_url}
            className="absolute inset-0 w-full h-full"
            allowFullScreen
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            title={`${title} - Episode ${episode}`}
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center bg-black">
            <p className="text-white/50">Tidak ada video yang tersedia</p>
          </div>
        )}
      </div>

      {/* Info bar */}
      <div className="mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-xl font-black text-white">{title}</h1>
          <p className="text-white/50 text-sm mt-0.5">Episode {episode}</p>
        </div>
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm font-medium hover:bg-white/10 transition self-start"
        >
          <i data-lucide="arrow-left" className="w-4 h-4" />Kembali
        </button>
      </div>

      {/* Server selector */}
      {availableServers.length > 1 && (
        <div className="mt-4">
          <p className="text-white/50 text-sm mb-2">Server:</p>
          <div className="flex flex-wrap gap-2">
            {SERVERS.map((srv) => (
              <button
                key={srv}
                onClick={() => handleServerChange(srv)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  currentServer === srv
                    ? "bg-donglyn/20 border border-donglyn/40 text-donglyn"
                    : "bg-white/5 border border-white/10 text-white/70 hover:border-white/20 hover:text-white"
                }`}
              >
                {srv}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Stream info */}
      {streamData && (
        <div className="mt-3 text-xs text-white/30">
          Server: {streamData.server} | Elapsed: {streamData.elapsed_time}
        </div>
      )}
    </div>
  );
}
