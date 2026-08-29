"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.forgotPassword({ email });
      setSent(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal mengirim email");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-72px)] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="inline-block">
            <img src="/logo.png" alt="Donglyn" className="h-10 w-auto mx-auto mb-3" />
          </Link>
          <h1 className="text-2xl font-black text-white">Lupa Password</h1>
          <p className="text-white/50 text-sm mt-1">Kami akan mengirim link reset ke emailmu</p>
        </div>

        {!sent ? (
          <form onSubmit={handleSubmit} className="bg-[#0d0d0d] border border-white/10 rounded-2xl p-6 space-y-4">
            {error && (
              <div className="px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                {error}
              </div>
            )}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-white/70 mb-1.5">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/30 focus:border-donglyn/60 focus:ring-2 focus:ring-donglyn/20 outline-none transition-all"
                placeholder="nama@email.com"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-xl bg-donglyn text-white font-black text-sm hover:bg-[#f40612] transition-all duration-200 disabled:opacity-50"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <i data-lucide="loader-2" className="w-4 h-4 animate-spin" />
                  Mengirim...
                </span>
              ) : (
                "Kirim Link Reset"
              )}
            </button>
          </form>
        ) : (
          <div className="bg-[#0d0d0d] border border-white/10 rounded-2xl p-6 text-center">
            <div className="w-16 h-16 rounded-full bg-green-500/20 border border-green-500/30 flex items-center justify-center mx-auto mb-4">
              <i data-lucide="check-circle" className="w-8 h-8 text-green-500" />
            </div>
            <p className="text-white/70 text-sm mb-2">Link reset telah dikirim ke</p>
            <p className="text-white font-bold mb-6">{email}</p>
            <Link
              href="/login"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white/10 border border-white/20 text-white font-bold text-sm hover:bg-white/15 transition"
            >
              <i data-lucide="arrow-left" className="w-4 h-4" />
              Kembali ke Login
            </Link>
          </div>
        )}

        <p className="text-center text-sm text-white/50 mt-6">
          Ingat password?{" "}
          <Link href="/login" className="text-donglyn hover:underline font-medium">
            Masuk
          </Link>
        </p>
      </div>
    </div>
  );
}
