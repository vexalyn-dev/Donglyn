import Link from "next/link";
import type { PosterCardData } from "@/lib/types";

interface PosterCardProps {
  data: PosterCardData;
  index?: number;
  showProgress?: boolean;
  progress?: number;
  badge?: string;
}

export default function PosterCard({ data, index, showProgress = false, progress = 0, badge }: PosterCardProps) {
  const badgeColor =
    data.status === "Ongoing"
      ? "bg-donglyn text-white"
      : data.status === "Completed"
        ? "bg-white/20 text-white/80"
        : "bg-white/10 text-white/60";

  return (
    <Link
      href={`/detail?url=${encodeURIComponent(data.url)}`}
      className="group block relative rounded-xl overflow-hidden bg-background-card border border-white/5 hover:border-white/10 transition-all duration-300 hover:shadow-cardHover hover:-translate-y-1"
    >
      {/* Poster Image */}
      <div className="relative aspect-[2/3] overflow-hidden">
        <img
          src={data.poster}
          alt={data.title}
          loading="lazy"
          decoding="async"
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-[1.03]"
        />

        {/* Hover overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

        {/* Play button */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300">
          <div className="w-12 h-12 rounded-full bg-donglyn flex items-center justify-center shadow-lg transform scale-75 group-hover:scale-100 transition-transform duration-300">
            <i data-lucide="play" className="w-5 h-5 text-white fill-white" />
          </div>
        </div>

        {/* Status badge */}
        {data.badge && (
          <div className={`absolute top-2 left-2 px-2 py-0.5 text-[10px] font-black rounded ${badgeColor}`}>
            {data.badge}
          </div>
        )}

        {/* Status dot */}
        {data.status && (
          <div className="absolute top-2 right-2 flex items-center gap-1 px-2 py-0.5 rounded-full bg-black/60 backdrop-blur-sm text-[10px] font-medium text-white/80">
            <span className={`w-1.5 h-1.5 rounded-full ${data.status === "Ongoing" ? "bg-donglyn animate-pulse" : "bg-white/60"}`} />
            {data.status}
          </div>
        )}
      </div>

      {/* Info */}
      <div className="p-3">
        <h3 className="text-white font-semibold text-sm leading-tight line-clamp-1 mb-1 group-hover:text-white/90 transition-colors">
          {data.title}
        </h3>
        <div className="flex items-center gap-2 text-[11px] text-white/50">
          {data.episode && (
            <span className="flex items-center gap-1">
              <i data-lucide="film" className="w-3 h-3" />
              {data.episode}
            </span>
          )}
          {data.rating && (
            <span className="flex items-center gap-0.5">
              <i data-lucide="star" className="w-3 h-3 text-yellow-500 fill-yellow-500" />
              {data.rating}
            </span>
          )}
        </div>

        {/* Progress bar */}
        {showProgress && (
          <div className="mt-2 h-1 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-donglyn rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
      </div>
    </Link>
  );
}
