import PosterCard from "./PosterCard";
import type { PosterCardData } from "@/lib/types";

interface ContentSectionProps {
  title: string;
  items: PosterCardData[];
  moreUrl?: string;
  skeletonCount?: number;
}

export default function ContentSection({ title, items, moreUrl, skeletonCount = 6 }: ContentSectionProps) {
  if (!items || items.length === 0) return null;

  return (
    <section className="py-6 md:py-8">
      {/* Section Header */}
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-xl md:text-2xl font-black text-white tracking-wide">{title}</h2>
        {moreUrl && (
          <a
            href={moreUrl}
            className="flex items-center gap-1 text-sm font-medium text-white/50 hover:text-donglyn transition-colors duration-200"
          >
            Lihat Semua
            <i data-lucide="arrow-right" className="w-4 h-4" />
          </a>
        )}
      </div>

      {/* Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
        {items.slice(0, 12).map((item, i) => (
          <PosterCard key={`${item.id || i}-${item.url}`} data={item} index={i} />
        ))}
      </div>
    </section>
  );
}
