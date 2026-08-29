"use client";

import { Suspense } from "react";
import ResetPasswordContent from "./ResetPasswordContent";

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div className="min-h-[calc(100vh-72px)] flex items-center justify-center"><div className="animate-pulse w-full max-w-md"><div className="h-8 bg-white/5 rounded mb-4" /><div className="h-12 bg-white/5 rounded mb-3" /><div className="h-12 bg-white/5 rounded mb-3" /><div className="h-12 bg-white/5 rounded" /></div></div>}>
      <ResetPasswordContent />
    </Suspense>
  );
}

export const dynamic = "force-dynamic";
