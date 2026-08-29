"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import PosterCard from "@/components/content/PosterCard";
import { EmptyState } from "@/components/ui/States";
import { api } from "@/lib/api";

export default function SearchContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") || "";
  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(!!initialQuery);

  useEffect(() => {
    if (initialQuery) performSearch(initialQuery);
  }, []);

  const performSearch = async (q: string) => {
    if (!q.trim()) return;
    setLoading(true);
    setHasSearched(true);
    try {
      const res = await api.search(q);
      setResults(res.results || []);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
      performSearch(query.trim());
    }
  };

  return (
    <div className="max-w-[1600px] mx-auto px-4 md:px-8 py-6">
      <form onSubmit={handleSubmit} className="mb-8">
        <div className="relative max-w-2xl">
          <i data-lucide="search" className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Cari judul donghua..."
            className="w-full pl-12 pr-4 py-3.5 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/30 focus:border-donglyn/60 focus:ring-2 focus:ring-donglyn/20 outline-none transition-all"
          />
          <button
            type="submit"
            className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2 px-4 py-2 rounded-lg bg-donglyn text-white text-sm font-black hover:bg-[#f40612] transition"
          >
            Cari
          </button>
        </div>
      </form>

      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="aspect-[2/3] rounded-xl bg-white/5 mb-3" />
              <div className="h-4 bg-white/5 rounded w-3/4 mb-2" />
              <div className="h-3 bg-white/5 rounded w-1/2" />
            </div>
          ))}
        </div>
      ) : hasSearched ? (
        results.length > 0 ? (
          <>
            <p className="text-white/50 text-sm mb-5">
              Ditemukan {results.length} hasil untuk &quot;{query}&quot;
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
              {results.map((item: any, i: number) => (
                <PosterCard key={`${item.id || i}-${item.url}`} data={item} index={i} />
              ))}
            </div>
          </>
        ) : (
          <EmptyState title="Tidak ada donghua ditemukan" description="Coba gunakan kata kunci lain atau periksa ejaannya." icon="search-x" />
        )
      ) : (
        <EmptyState title="Cari Donghua Favoritmu" description="Masukkan judul di atas untuk memulai pencarian." icon="search" />
      )}
    </div>
  );
}
