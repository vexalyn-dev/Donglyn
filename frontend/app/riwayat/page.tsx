"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import PosterCard from "@/components/content/PosterCard";
import { EmptyState } from "@/components/ui/States";
import { api } from "@/lib/api";
import type { HistoryItem, UserData } from "@/lib/types";

export default function RiwayatPage() {
  const router = useRouter();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<UserData | null>(null);

  useEffect(() => {
    api
      .getMe()
      .then((res: { logged_in: boolean; user: UserData | null }) => {
        if (!res.logged_in) {
          router.push("/login");
          return;
        }
        setUser(res.user);
        return api.getHistory();
      })
      .then((res: HistoryItem[] | undefined) => {
        if (res) setHistory(res);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  const handlePlay = (item: HistoryItem) => {
    router.push(`/detail?url=${encodeURIComponent(item.url)}`);
  };

  const handleRemove = async (item: HistoryItem) => {
    try {
      await api.deleteHistoryItem({ donghua_id: item.donghua_id });
      setHistory((prev) => prev.filter((h) => h.donghua_id !== item.donghua_id));
    } catch {
      // ignore
    }
  };

  if (loading) {
    return (
      <div className="max-w-[1600px] mx-auto px-4 md:px-8 py-6">
        <h1 className="text-2xl font-black text-white mb-6">Riwayat</h1>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="aspect-[2/3] rounded-xl bg-white/5 mb-3" />
              <div className="h-4 bg-white/5 rounded w-3/4 mb-2" />
              <div className="h-3 bg-white/5 rounded w-1/2" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-[1600px] mx-auto px-4 md:px-8 py-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-black text-white">Riwayat</h1>
        {history.length > 0 && (
          <button
            onClick={() => {
              if (confirm("Hapus semua riwayat?")) {
                api.clearHistory().then(() => setHistory([]));
              }
            }}
            className="text-sm text-white/50 hover:text-red-500 transition-colors"
          >
            Hapus Semua
          </button>
        )}
      </div>

      {history.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {history.map((item) => (
            <div key={item.donghua_id} className="relative group">
              <PosterCard
                data={{
                  id: item.donghua_id,
                  title: item.title,
                  url: item.url,
                  poster: item.poster,
                  episode: item.episode,
                  status: undefined,
                }}
                showProgress
                progress={item.progress || 0}
              />
              <button
                onClick={() => handlePlay(item)}
                className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <div className="w-12 h-12 rounded-full bg-donglyn flex items-center justify-center shadow-lg">
                  <i data-lucide="play" className="w-5 h-5 text-white fill-white" />
                </div>
              </button>
              <button
                onClick={() => handleRemove(item)}
                className="absolute top-2 right-2 w-8 h-8 rounded-full bg-black/70 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                aria-label="Hapus dari riwayat"
              >
                <i data-lucide="trash-2" className="w-4 h-4 text-red-500" />
              </button>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState
          title="Belum ada riwayat"
          description="Mulai nonton donghua untuk melihat riwayatmu di sini."
          icon="history"
        />
      )}
    </div>
  );
}
