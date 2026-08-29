"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import PosterCard from "@/components/content/PosterCard";
import { SkeletonGrid } from "@/components/ui/States";
import { api } from "@/lib/api";
import type { GenreItem, PosterCardData } from "@/lib/types";

export default function GenrePage() {
  const [genres, setGenres] = useState<GenreItem[]>([]);
  const [selectedGenre, setSelectedGenre] = useState<string | null>(null);
  const [items, setItems] = useState<PosterCardData[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getGenres().then((res) => setGenres(res.genres || [])).catch(() => {});
  }, []);

  useEffect(() => {
    if (!selectedGenre) {
      setItems([]);
      return;
    }
    setLoading(true);
    api
      .getGenre(selectedGenre)
      .then((res) => setItems(res.data || []))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, [selectedGenre]);

  return (
    <div className="max-w-[1600px] mx-auto px-4 md:px-8 py-6">
      <h1 className="text-2xl md:text-3xl font-black text-white mb-6">Genre</h1>

      {/* Genre Pills */}
      <div className="flex flex-wrap gap-2 mb-8">
        <button
          onClick={() => setSelectedGenre(null)}
          className={`px-4 py-2 rounded-full text-sm font-bold transition-all ${
            !selectedGenre
              ? "bg-donglyn text-white"
              : "bg-white/5 border border-white/10 text-white/70 hover:border-donglyn/40 hover:text-white"
          }`}
        >
          Semua
        </button>
        {genres.map((genre) => (
          <button
            key={genre.slug}
            onClick={() => setSelectedGenre(genre.slug)}
            className={`px-4 py-2 rounded-full text-sm font-bold transition-all ${
              selectedGenre === genre.slug
                ? "bg-donglyn text-white"
                : "bg-white/5 border border-white/10 text-white/70 hover:border-donglyn/40 hover:text-white"
            }`}
          >
            {genre.name}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading ? (
        <SkeletonGrid count={12} />
      ) : items.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {items.map((item, i) => (
            <PosterCard key={`${item.id || i}-${item.url}`} data={item} index={i} />
          ))}
        </div>
      ) : selectedGenre ? (
        <div className="text-center py-20">
          <p className="text-white/50">Tidak ada konten untuk genre ini.</p>
        </div>
      ) : (
        <div className="text-center py-20">
          <p className="text-white/40">Pilih genre untuk memulai</p>
        </div>
      )}
    </div>
  );
}
