"use client";

import { useEffect, useState } from "react";

export default function LoadingScreen() {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
    }, 800);
    return () => clearTimeout(timer);
  }, []);

  if (!visible) return null;

  return (
    <div
      id="splash"
      className="fixed inset-0 z-[9999] bg-black flex flex-col items-center justify-center transition-all duration-600 ease-[cubic-bezier(.4,0,.2,1)]"
      style={{ opacity: 1, visibility: "visible", pointerEvents: "auto" }}
    >
      {/* Background gradient */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_40%,rgba(229,9,20,.06)_0%,transparent_60%)]" />
        <div
          className="absolute inset-0"
          style={{
            backgroundImage:
              "linear-gradient(rgba(255,255,255,.015) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.015) 1px,transparent 1px)",
            backgroundSize: "48px 48px",
            animation: "gridMove 20s linear infinite",
          }}
        />
      </div>

      {/* Content */}
      <div className="relative z-10 text-center flex flex-col items-center">
        {/* Logo */}
        <div className="relative mb-8">
          <img
            src="/logo.png"
            alt="Donglyn"
            className="w-[clamp(140px,30vw,220px)] h-auto object-contain"
            style={{ animation: "logoIn .7s cubic-bezier(.22,.61,.36,1) both", filter: "drop-shadow(0 0 34px rgba(229,9,20,.42))" }}
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = "none";
              const fallback = document.getElementById("splashFallback");
              if (fallback) fallback.classList.add("visible");
            }}
          />
          <div
            className="absolute -inset-4 border border-donglyn/15 rounded-full"
            style={{ animation: "ringPulse 3s ease-in-out infinite" }}
          />
          <div
            id="splashFallback"
            className="hidden font-display text-[48px] tracking-[.15em] text-white"
            style={{ filter: "drop-shadow(0 0 20px rgba(229,9,20,.4))" }}
          >
            DONGLYN
          </div>
        </div>

        {/* Divider */}
        <div
          className="w-10 h-px mb-6"
          style={{
            background: "linear-gradient(90deg,transparent,rgba(229,9,20,.6),transparent)",
            animation: "divIn .6s .2s ease both",
          }}
        />

        {/* Progress bar */}
        <div
          className="w-40 h-px bg-white/10 rounded-full overflow-hidden"
          style={{ animation: "barIn .6s .35s ease both" }}
        >
          <div
            className="h-full bg-gradient-to-r from-donglyn to-[#ff6b6b] rounded-full"
            style={{ width: "100%", animation: "splashBarSweep 1.15s ease-in-out infinite alternate" }}
          />
        </div>

        {/* Status text */}
        <p
          className="mt-4 text-[11px] font-medium text-white/25 tracking-[.08em]"
          style={{ animation: "statusIn .6s .5s ease both" }}
        >
          Memuat
        </p>
      </div>

      {/* Keyframes */}
      <style>{`
        @keyframes gridMove {
          from { transform: translateY(0); }
          to { transform: translateY(48px); }
        }
        @keyframes logoIn {
          from { opacity: 0; transform: translateY(30px) scale(.9); }
          to { opacity: 1; transform: translateY(0) scale(1); }
        }
        @keyframes ringPulse {
          0%, 100% { transform: scale(1); opacity: .3; }
          50% { transform: scale(1.08); opacity: .6; }
        }
        @keyframes divIn {
          from { opacity: 0; width: 0; }
          to { opacity: 1; width: 40px; }
        }
        @keyframes barIn {
          from { opacity: 0; transform: scaleX(0); }
          to { opacity: 1; transform: scaleX(1); }
        }
        @keyframes splashBarSweep {
          from { transform: translateX(-120%); }
          to { transform: translateX(290%); }
        }
        @keyframes statusIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
