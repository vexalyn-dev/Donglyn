"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getMe().then((res) => {
      if (res.logged_in) router.replace("/");
    }).catch(() => {});
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Password tidak cocok");
      return;
    }
    if (password.length < 6) {
      setError("Password minimal 6 karakter");
      return;
    }

    setLoading(true);
    try {
      await api.register({ email, password, username });
      router.push("/verify-email-sent");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registrasi gagal");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-72px)] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-block">
            <img src="/logo.png" alt="Donglyn" className="h-10 w-auto mx-auto mb-3" />
          </Link>
          <h1 className="text-2xl font-black text-white">Daftar</h1>
          <p className="text-white/50 text-sm mt-1">Buat akun untuk mulai streaming</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-[#0d0d0d] border border-white/10 rounded-2xl p-6 space-y-4">
          {error && (
            <div className="px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
              {error}
            </div>
          )}

          <div>
            <label htmlFor="username" className="block text-sm font-medium text-white/70 mb-1.5">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/30 focus:border-donglyn/60 focus:ring-2 focus:ring-donglyn/20 outline-none transition-all"
              placeholder="nama_pengguna"
            />
          </div>

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

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-white/70 mb-1.5">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/30 focus:border-donglyn/60 focus:ring-2 focus:ring-donglyn/20 outline-none transition-all"
              placeholder="••••••••"
            />
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-white/70 mb-1.5">
              Konfirmasi Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/30 focus:border-donglyn/60 focus:ring-2 focus:ring-donglyn/20 outline-none transition-all"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 rounded-xl bg-donglyn text-white font-black text-sm hover:bg-[#f40612] transition-all duration-200 hover:-translate-y-0.5 hover:shadow-[0_8px_24px_rgba(229,9,20,.4)] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <i data-lucide="loader-2" className="w-4 h-4 animate-spin" />
                Mendaftarkan...
              </span>
            ) : (
              "DAFTAR"
            )}
          </button>
        </form>

        <p className="text-center text-sm text-white/50 mt-6">
          Sudah punya akun?{" "}
          <Link href="/login" className="text-donglyn hover:underline font-medium">
            Masuk
          </Link>
        </p>
      </div>
    </div>
  );
}
