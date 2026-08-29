"use client";

import { useEffect, useState } from "react";
import HeroBanner from "@/components/content/HeroBanner";
import ContentSection from "@/components/content/ContentSection";
import { SkeletonGrid } from "@/components/ui/States";
import { api } from "@/lib/api";
import type { HomeData } from "@/lib/types";

export default function Home() {
  const [data, setData] = useState<HomeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await api.getHome();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    // Re-init Lucide icons after content loads
    if (typeof window !== "undefined" && (window as any).lucide) {
      (window as any).lucide.createIcons();
    }
  }, [data, loading]);

  if (loading) {
    return (
      <div className="max-w-[1600px] mx-auto px-4 md:px-8 py-6">
        {/* Hero skeleton */}
        <div className="relative h-[50vh] md:h-[60vh] lg:h-[70vh] max-h-[600px] rounded-2xl overflow-hidden mb-8">
          <div className="absolute inset-0 bg-white/5 animate-pulse rounded-2xl" />
        </div>

        {/* Sections skeleton */}
        <div className="space-y-8">
          {[1, 2, 3].map((i) => (
            <div key={i}>
              <div className="h-7 w-48 bg-white/5 rounded mb-5 animate-pulse" />
              <SkeletonGrid count={6} />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-[1600px] mx-auto px-4 md:px-8 py-20 text-center">
        <div className="w-16 h-16 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto mb-4">
          <i data-lucide="alert-circle" className="w-8 h-8 text-red-500" />
        </div>
        <p className="text-white/70 text-sm mb-4">{error || "Gagal memuat konten"}</p>
        <button
          onClick={() => window.location.reload()}
          className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 border border-white/20 text-white text-sm font-medium hover:bg-white/15 transition mx-auto"
        >
          <i data-lucide="refresh-cw" className="w-4 h-4" />
          Coba Lagi
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-[1600px] mx-auto px-4 md:px-8 py-6">
      {/* Hero Banner */}
      <HeroBanner banners={data.banners} loading={false} />

      {/* Content Sections */}
      <div className="mt-8 space-y-2">
        {data.sections.map((section) => (
          <ContentSection
            key={section.section_name}
            title={section.section_name}
            items={section.data}
            moreUrl={section.archive_url}
          />
        ))}
      </div>

      {/* Genres section */}
      {data.genres && data.genres.length > 0 && (
        <section className="py-6 md:py-8">
          <h2 className="text-xl md:text-2xl font-black text-white tracking-wide mb-5">Genre</h2>
          <div className="flex flex-wrap gap-2">
            {data.genres.map((genre) => (
              <a
                key={genre.slug}
                href={`/genre/${genre.slug}`}
                className="px-4 py-2 rounded-full bg-white/5 border border-white/10 text-white/70 text-sm font-medium hover:border-donglyn/40 hover:text-white hover:bg-donglyn/10 transition-all duration-200"
              >
                {genre.name}
              </a>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
