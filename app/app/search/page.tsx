"use client";

import { Suspense } from "react";
import SearchContent from "./SearchContent";

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="max-w-[1600px] mx-auto px-4 md:px-8 py-6"><div className="animate-pulse h-12 bg-white/5 rounded mb-6" /><div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">{Array.from({ length: 12 }).map((_, i) => (<div key={i} className="animate-pulse"><div className="aspect-[2/3] rounded-xl bg-white/5 mb-3" /><div className="h-4 bg-white/5 rounded w-3/4 mb-2" /><div className="h-3 bg-white/5 rounded w-1/2" /></div>))}</div></div>}>
      <SearchContent />
    </Suspense>
  );
}

export const dynamic = "force-dynamic";
