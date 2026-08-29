"use client";

import { Suspense } from "react";
import VerifyEmailContent from "./VerifyEmailContent";

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div className="min-h-[calc(100vh-72px)] flex items-center justify-center"><div className="animate-pulse w-16 h-16 rounded-full bg-white/5" /></div>}>
      <VerifyEmailContent />
    </Suspense>
  );
}

export const dynamic = "force-dynamic";
