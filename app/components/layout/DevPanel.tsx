"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export default function DevPanel() {
  const [open, setOpen] = useState(false);
  const [passcode, setPasscode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await api.devLogin({ username: "donglyn_dev", password: passcode });
      if (res.success) {
        window.location.href = "/dev-panel";
      } else {
        setError("Passcode salah");
      }
    } catch {
      setError("Gagal terhubung ke server");
    } finally {
      setLoading(false);
    }
  };

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-4 right-4 w-8 h-8 rounded-full bg-white/5 border border-white/10 flex items-center justify-center hover:border-donglyn/60 hover:shadow-[0_0_18px_rgba(229,9,20,.25)] transition-all duration-200 z-40"
        aria-label="Dev panel"
        title="Developer Access"
      >
        <i data-lucide="terminal" className="w-3.5 h-3.5 text-white/40" />
      </button>
    );
  }

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 z-[100] bg-[rgba(4,7,10,.82)] backdrop-blur-md flex items-center justify-center"
        onClick={() => setOpen(false)}
      >
        {/* Panel */}
        <div
          className="relative w-[min(90vw,420px)] bg-gradient-to-br from-[rgba(22,26,28,.96)] to-[rgba(8,10,11,.98)] border border-[rgba(206,220,227,.24)] rounded-xl shadow-[0_25px_80px_rgba(0,0,0,.55),inset_0_1px_0_rgba(255,255,255,.05)] p-7"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Close button */}
          <button
            onClick={() => setOpen(false)}
            className="absolute top-4 right-4 w-8 h-8 border border-[rgba(206,220,227,.18)] rounded-md bg-[rgba(206,220,227,.06)] text-[rgba(229,237,241,.75)] text-xl leading-none cursor-pointer hover:text-white transition-colors"
            aria-label="Close"
          >
            &times;
          </button>

          {/* Header */}
          <div className="text-[10px] font-black uppercase tracking-[.28em] text-red-400">
            Vexalyn Dev
          </div>
          <h2 className="mt-2 text-xl font-black text-white">Secret Access</h2>
          <p className="mt-2 text-sm text-white/60">
            Masukkan passcode untuk membuka Developer Dashboard.
          </p>

          {/* Form */}
          <form onSubmit={handleSubmit} className="mt-5">
            <label htmlFor="devPasscode" className="text-xs uppercase tracking-[.2em] text-white/45">
              Passcode
            </label>
            <input
              id="devPasscode"
              type="password"
              value={passcode}
              onChange={(e) => setPasscode(e.target.value)}
              placeholder="Masukkan secret key"
              autoComplete="off"
              required
              className="w-full mt-2 px-3.5 py-3 rounded-lg border border-[rgba(206,220,227,.2)] bg-[#030506] text-white outline-none focus:border-[rgba(229,237,241,.68)] focus:shadow-[0_0_0_3px_rgba(229,237,241,.09)] transition-all"
            />

            {error && (
              <div className="mt-3 rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-xs text-red-200">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-4 py-3 border border-white/35 rounded-lg bg-gradient-to-br from-[#dce6ea] to-[#77858d] text-[#0b0e0f] font-black cursor-pointer transition-all duration-200 hover:from-[#f4f8f9] hover:to-[#9eabb1] disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_8px_20px_rgba(0,0,0,.28),inset_0_1px_0_rgba(255,255,255,.4)]"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <i data-lucide="loader-2" className="w-4 h-4 animate-spin" />
                  Verifying...
                </span>
              ) : (
                "Unlock Dev Panel"
              )}
            </button>
          </form>
        </div>
      </div>
    </>
  );
}
