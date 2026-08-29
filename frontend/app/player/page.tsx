"use client";

import { Suspense } from "react";
import PlayerContent from "./PlayerContent";

export default function PlayerPage() {
  return (
    <Suspense fallback={<div className="max-w-[1600px] mx-auto px-4 md:px-8 py-4"><div className="animate-pulse aspect-video bg-white/5 rounded-xl" /></div>}>
      <PlayerContent />
    </Suspense>
  );
}

export const dynamic = "force-dynamic";
