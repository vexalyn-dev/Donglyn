export default function ErrorState({
  message = "Something went wrong.",
  onRetry,
}: {
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[300px] text-center px-4">
      <div className="w-16 h-16 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center mb-4">
        <i data-lucide="alert-circle" className="w-8 h-8 text-red-500" />
      </div>
      <p className="text-white/70 text-sm mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 border border-white/20 text-white text-sm font-medium hover:bg-white/15 transition"
        >
          <i data-lucide="refresh-cw" className="w-4 h-4" />
          Coba Lagi
        </button>
      )}
    </div>
  );
}

export function EmptyState({
  title = "Tidak ada konten",
  description = "Coba ubah filter atau pencarianmu.",
  icon = "search",
}: {
  title?: string;
  description?: string;
  icon?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[300px] text-center px-4">
      <div className="w-16 h-16 rounded-full bg-white/5 border border-white/10 flex items-center justify-center mb-4">
        <i data-lucide={icon} className="w-8 h-8 text-white/30" />
      </div>
      <p className="text-white/80 font-semibold text-base mb-1">{title}</p>
      <p className="text-white/40 text-sm">{description}</p>
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="animate-pulse">
      <div className="aspect-[2/3] rounded-xl bg-white/5 mb-3" />
      <div className="h-4 bg-white/5 rounded w-3/4 mb-2" />
      <div className="h-3 bg-white/5 rounded w-1/2" />
    </div>
  );
}

export function SkeletonGrid({ count = 8 }: { count?: number }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}
