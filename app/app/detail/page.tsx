"use client";

import { Suspense } from "react";
import DetailContent from "./DetailContent";

export default function DetailPage() {
  return (
    <Suspense fallback={<div className="max-w-[1600px] mx-auto px-4 md:px-8 py-6"><div className="animate-pulse h-96 bg-white/5 rounded-2xl mb-6" /><div className="grid grid-cols-[200px_1fr] gap-6"><div className="aspect-[2/3] bg-white/5 rounded-xl" /><div className="space-y-4"><div className="h-8 bg-white/5 rounded w-3/4" /><div className="h-4 bg-white/5 rounded w-1/2" /><div className="h-20 bg-white/5 rounded" /></div></div></div>}>
      <DetailContent />
    </Suspense>
  );
}

export const dynamic = "force-dynamic";
