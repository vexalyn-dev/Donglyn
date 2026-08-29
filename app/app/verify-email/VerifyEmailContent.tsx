"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";

export default function VerifyEmailContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token") || "";
  const [status, setStatus] = useState<"loading" | "success" | "invalid" | "expired">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) { setStatus("invalid"); setMessage("Token tidak ditemukan"); return; }
    fetch(`/api/auth/verify-email?token=${token}`, { credentials: "include" })
      .then((r) => r.json())
      .then((data) => {
        if (data.verified) { setStatus("success"); setMessage("Email berhasil diverifikasi! Kamu bisa login sekarang."); setTimeout(() => router.push("/login"), 3000); }
        else { setStatus("invalid"); setMessage(data.message || "Token tidak valid"); }
      })
      .catch(() => { setStatus("expired"); setMessage("Token sudah expired, silakan daftar ulang"); });
  }, [token, router]);

  return (
    <div className="min-h-[calc(100vh-72px)] flex items-center justify-center px-4">
      <div className="w-full max-w-md text-center">
        <div className={`w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center ${status === "success" ? "bg-green-500/20 border border-green-500/30" : status === "invalid" || status === "expired" ? "bg-red-500/20 border border-red-500/30" : "bg-white/5 border border-white/10"}`}>
          <i data-lucide={status === "success" ? "check-circle" : status === "loading" ? "loader-2" : "alert-circle"} className={`w-8 h-8 ${status === "success" ? "text-green-500 animate-spin" : status === "loading" ? "text-white/50 animate-spin" : "text-red-500"}`} />
        </div>
        <h1 className="text-2xl font-black text-white mb-2">{status === "loading" ? "Memverifikasi..." : status === "success" ? "Berhasil!" : "Gagal"}</h1>
        <p className="text-white/60 text-sm mb-6">{message}</p>
        <Link href="/login" className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-donglyn text-white font-black text-sm hover:bg-[#f40612] transition">
          <i data-lucide="log-in" className="w-4 h-4" />Login Sekarang
        </Link>
      </div>
    </div>
  );
}
