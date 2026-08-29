"use client";

import { useEffect, useState } from "react";
import PosterCard from "@/components/content/PosterCard";
import { SkeletonGrid } from "@/components/ui/States";
import { api } from "@/lib/api";
import type { PosterCardData } from "@/lib/types";

export default function TerbaruPage() {
  const [items, setItems] = useState<PosterCardData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getTerbaru()
      .then((res: any) => setItems(res.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-[1600px] mx-auto px-4 md:px-8 py-6">
      <h1 className="text-2xl md:text-3xl font-black text-white mb-6">Terbaru</h1>

      {loading ? (
        <SkeletonGrid count={12} />
      ) : items.length > 0 ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {items.map((item, i) => (
            <PosterCard key={`${item.id || i}-${item.url}`} data={item} index={i} showProgress badge={item.episode === "NEW" ? "NEW" : undefined} />
          ))}
        </div>
      ) : (
        <div className="text-center py-20">
          <p className="text-white/50">Tidak ada konten terbaru</p>
        </div>
      )}
    </div>
  );
}
