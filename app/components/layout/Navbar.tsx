"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { api } from "@/lib/api";
import type { UserData } from "@/lib/types";

interface NavbarProps {}

export default function Navbar({}: NavbarProps) {
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [user, setUser] = useState<UserData | null>(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);

  const navItems = [
    { href: "/", label: "Beranda", icon: "home" },
    { href: "/genre", label: "Genre", icon: "layers" },
    { href: "/schedule", label: "Schedule", icon: "calendar" },
    { href: "/terbaru", label: "Terbaru", icon: "zap" },
  ];

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    const initAuth = async () => {
      try {
        const data = await api.getMe();
        setUser(data.user || null);
      } catch {
        setUser(null);
      }
    };
    initAuth();
  }, []);

  const handleSearch = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (searchQuery.trim()) {
      window.location.href = `/search?q=${encodeURIComponent(searchQuery.trim())}`;
    }
  };

  const handleLogout = async () => {
    try {
      await api.logout();
    } catch {
      // ignore
    }
    setUser(null);
    setDropdownOpen(false);
    window.location.href = "/";
  };

  return (
    <>
      <nav
        id="donglynNav"
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled
            ? "bg-[rgba(10,10,10,.97)] border-b border-white/10 shadow-[0_1px_0_rgba(255,255,255,.04),0_4px_24px_rgba(0,0,0,.4)] backdrop-blur-md"
            : "bg-gradient-to-b from-black/80 via-black/60 to-transparent border-b border-transparent"
        }`}
      >
        <div className="max-w-[1600px] mx-auto px-4 md:px-8 py-3.5 flex items-center justify-between gap-4">
          {/* Logo + Desktop Nav */}
          <div className="flex items-center gap-6">
            <Link href="/" className="flex-shrink-0" id="donglynSecretTrigger">
              <img
                src="/logo.png"
                alt="Donglyn"
                className="h-9 md:h-11 lg:h-12 w-auto object-contain max-h-[56px]"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = "none";
                }}
              />
            </Link>

            {/* Desktop Nav */}
            <div className="hidden lg:flex items-center gap-5 text-[13px] font-medium nav-wrap relative">
              {navItems.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`pb-1 border-b-2 transition-all duration-200 flex items-center gap-1.5 ${
                      isActive
                        ? "text-white border-donglyn"
                        : "text-white/70 hover:text-white border-transparent hover:border-white/30"
                    }`}
                    data-nav={item.href.replace("/", "")}
                  >
                    <i
                      data-lucide={item.icon}
                      className={`w-4 h-4 ${
                        isActive ? "text-donglyn" : ""
                      } ${item.icon === "home" ? "icon-bounce" : item.icon === "layers" ? "icon-pulse" : item.icon === "calendar" ? "icon-spin-hover" : "icon-shimmer"}`}
                    />
                    {item.label}
                  </Link>
                );
              })}
              <div className="nav-indicator absolute bottom-0 h-0.5 bg-donglyn rounded transition-all duration-350 ease-[cubic-bezier(.4,0,.2,1)] shadow-[0_0_10px_rgba(229,9,20,.7),0_0_20px_rgba(229,9,20,.3)] pointer-events-none" />
            </div>
          </div>

          {/* Right Side: Search + Auth */}
          <div className="flex items-center gap-3 order-last lg:order-none">
            {/* Desktop Search */}
            <form
              onSubmit={handleSearch}
              className="hidden md:flex items-center gap-0 desktop-search"
            >
              <div className="desktop-search-inner flex items-center gap-2 px-3 py-1.5 bg-[rgba(25,25,25,.92)] border border-white/10 rounded-full transition-all duration-300 focus-within:border-[rgba(229,9,20,.65)] focus-within:shadow-[0_0_0_3px_rgba(229,9,20,.12),0_10px_28px_rgba(0,0,0,.28)]">
                <i data-lucide="search" className="w-4 h-4 text-white/50 flex-shrink-0 transition-colors duration-250 focus-within:text-donglyn" />
                <input
                  type="text"
                  placeholder="Cari judul donghua..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="bg-transparent border-0 outline-none text-white text-[13px] font-medium w-[200px] focus:w-[280px] transition-[width] duration-300 placeholder:text-white/38"
                  aria-label="Cari judul donghua"
                />
                <button
                  type="submit"
                  className="flex items-center gap-1.5 flex-shrink-0 h-8 px-3 border-0 rounded-full bg-donglyn text-white text-[11px] font-black tracking-[.02em] cursor-pointer transition-all duration-200 hover:bg-[#f40612] hover:-translate-y-0.5 active:translate-y-0"
                >
                  <span>CARI</span>
                  <i data-lucide="arrow-right" className="w-3 h-3" />
                </button>
              </div>
            </form>

            {/* Mobile Search Button */}
            <Link
              href="/search"
              className="md:hidden w-9 h-9 flex items-center justify-center border border-white/10 rounded-lg bg-white/5 hover:bg-white/10 transition"
              aria-label="Cari"
            >
              <i data-lucide="search" className="w-4 h-4 text-white/70" />
            </Link>

            {/* Auth Buttons */}
            {!user ? (
              <Link
                href="/login"
                className="hidden lg:inline-flex items-center justify-center h-8 px-3.5 border-0 rounded-full bg-donglyn text-white text-[11px] font-black tracking-[.02em] cursor-pointer transition-all duration-200 hover:bg-[#b20710] hover:-translate-y-0.5 shadow-[0_2px_12px_rgba(229,9,20,.35)]"
              >
                Masuk
              </Link>
            ) : (
              <div ref={dropdownRef} className="relative">
                <button
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                  className="flex items-center gap-2 group"
                  aria-label="User menu"
                >
                  <div className="guest-profile-icon w-8 h-8 border border-donglyn/35 rounded-full bg-donglyn/10 text-donglyn transition-all duration-250 group-hover:-translate-y-0.5 group-hover:bg-donglyn/18 group-hover:shadow-[0_0_0_4px_rgba(229,9,20,.08),0_8px_18px_rgba(0,0,0,.25)]">
                    <i data-lucide="user" className="w-4 h-4" />
                  </div>
                </button>

                {/* Dropdown */}
                <div
                  className={`absolute top-full right-0 mt-2 w-56 bg-[#0d0d0d] border border-white/10 rounded-lg shadow-2xl overflow-hidden user-dropdown transition-all duration-200 ${
                    dropdownOpen
                      ? "opacity-100 translate-y-0 scale-100 pointer-events-auto"
                      : "opacity-0 -translate-y-2 scale-97 pointer-events-none"
                  }`}
                >
                  {/* User Info */}
                  <div className="flex items-center gap-3 px-4 py-3 border-b border-white/10">
                    <div className="w-10 h-10 rounded-full bg-donglyn/10 border border-donglyn/35 flex items-center justify-center text-donglyn flex-shrink-0">
                      <i data-lucide="user" className="w-5 h-5" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-bold truncate text-white">
                        {user.username || "User"}
                      </p>
                      <p className="text-[11px] text-white/50 truncate">{user.email}</p>
                    </div>
                  </div>

                  {/* Links */}
                  <div className="py-1">
                    <Link
                      href="/bookmark"
                      className="flex items-center gap-3 px-4 py-2.5 text-sm font-bold text-white/80 hover:bg-white/5 transition"
                      onClick={() => setDropdownOpen(false)}
                    >
                      <i data-lucide="bookmark" className="w-5 text-donglyn flex-shrink-0" />
                      Bookmark
                    </Link>
                    <Link
                      href="/riwayat"
                      className="flex items-center gap-3 px-4 py-2.5 text-sm font-bold text-white/80 hover:bg-white/5 transition"
                      onClick={() => setDropdownOpen(false)}
                    >
                      <i data-lucide="history" className="w-5 text-donglyn flex-shrink-0" />
                      Riwayat
                    </Link>
                    <Link
                      href="/profile"
                      className="flex items-center gap-3 px-4 py-2.5 text-sm font-bold text-white/80 hover:bg-white/5 transition"
                      onClick={() => setDropdownOpen(false)}
                    >
                      <i data-lucide="settings" className="w-5 text-donglyn flex-shrink-0" />
                      Settings
                    </Link>
                    <div className="border-t border-white/10 my-1" />
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-sm font-bold text-donglyn hover:bg-white/5 transition text-left"
                    >
                      <i data-lucide="log-out" className="w-5 flex-shrink-0" />
                      Keluar
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="lg:hidden w-9 h-9 flex items-center justify-center border border-white/10 rounded-lg bg-white/5 hover:bg-white/10 transition relative"
              aria-label="Buka menu"
            >
              <span
                className={`absolute w-4 h-[2px] bg-white/80 rounded left-1/2 -translate-x-1/2 transition-all duration-300 ${
                  mobileOpen ? "top-1/2 -translate-y-1/2 rotate-45" : "top-[7px]"
                }`}
              />
              <span
                className={`absolute w-4 h-[2px] bg-white/80 rounded left-1/2 -translate-x-1/2 transition-all duration-300 ${
                  mobileOpen ? "opacity-0 scale-x-0" : "top-[14px]"
                }`}
              />
              <span
                className={`absolute w-4 h-[2px] bg-white/80 rounded left-1/2 -translate-x-1/2 transition-all duration-300 ${
                  mobileOpen ? "top-1/2 -translate-y-1/2 -rotate-45" : "top-[21px]"
                }`}
              />
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile Menu Overlay */}
      <div
        className={`fixed inset-0 z-[199] bg-black/60 backdrop-blur-sm transition-opacity duration-400 ${
          mobileOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        }`}
        onClick={() => setMobileOpen(false)}
      />

      {/* Mobile Menu */}
      <div
        className={`fixed bottom-0 left-0 right-0 z-[200] max-h-[70vh] bg-gradient-to-t from-[#0a0a0a] to-[#141414] border-t border-donglyn/20 rounded-t-[24px] overflow-hidden flex flex-col transition-transform duration-500 ease-[cubic-bezier(.32,.72,0,1)] shadow-[0_-8px_40px_rgba(0,0,0,.6),0_-2px_0_rgba(229,9,20,.1)] ${
          mobileOpen ? "translate-y-0" : "translate-y-full"
        }`}
      >
        {/* Drag handle */}
        <div className="w-10 h-1 bg-white/20 rounded-full mx-auto mt-3 flex-shrink-0" />

        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-white/10 flex-shrink-0">
          <Link href="/" onClick={() => setMobileOpen(false)}>
            <img
              src="/logo.png"
              alt="Donglyn"
              className="h-7 w-auto object-contain"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = "none";
              }}
            />
          </Link>
          <button
            onClick={() => setMobileOpen(false)}
            className="w-8 h-8 flex items-center justify-center border border-white/10 rounded hover:bg-white/10 transition"
            aria-label="Tutup menu"
          >
            <i data-lucide="x" className="w-4 h-4" />
          </button>
        </div>

        {/* Nav Items */}
        <div className="flex-1 overflow-y-auto py-2">
          <Link
            href="/search"
            onClick={() => setMobileOpen(false)}
            className="flex items-center gap-3 px-5 py-3 text-sm font-bold text-white/70 hover:text-white hover:bg-white/5 transition"
          >
            <i data-lucide="search" className="w-5" />
            Cari
          </Link>
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMobileOpen(false)}
              className={`flex items-center gap-3 px-5 py-3 text-sm font-bold transition border-l-3 ${
                pathname === item.href
                  ? "text-white bg-white/5 border-donglyn"
                  : "text-white/70 hover:text-white hover:bg-white/5 border-transparent"
              }`}
            >
              <i data-lucide={item.icon} className="w-5" />
              {item.label}
            </Link>
          ))}

          {!user ? (
            <>
              <div className="border-t border-white/10 my-2" />
              <Link
                href="/login"
                onClick={() => setMobileOpen(false)}
                className="flex items-center gap-3 px-5 py-3 text-sm font-bold text-white/70 hover:bg-white/5 transition"
              >
                <i data-lucide="log-in" className="w-5 text-white/50" />
                Masuk
              </Link>
              <Link
                href="/register"
                onClick={() => setMobileOpen(false)}
                className="flex items-center gap-3 px-5 py-3 text-sm font-bold text-white/70 hover:bg-white/5 transition"
              >
                Daftar
              </Link>
            </>
          ) : (
            <>
              <div className="border-t border-white/10 my-2" />
              <Link
                href="/bookmark"
                onClick={() => setMobileOpen(false)}
                className="flex items-center gap-3 px-5 py-3 text-sm font-bold text-white/70 hover:text-white hover:bg-white/5 transition"
              >
                <i data-lucide="bookmark" className="w-5" />
                Bookmark
              </Link>
              <Link
                href="/riwayat"
                onClick={() => setMobileOpen(false)}
                className="flex items-center gap-3 px-5 py-3 text-sm font-bold text-white/70 hover:text-white hover:bg-white/5 transition"
              >
                <i data-lucide="history" className="w-5" />
                Riwayat
              </Link>
              <Link
                href="/profile"
                onClick={() => setMobileOpen(false)}
                className="flex items-center gap-3 px-5 py-3 text-sm font-bold text-white/70 hover:text-white hover:bg-white/5 transition"
              >
                <i data-lucide="settings" className="w-5" />
                Settings
              </Link>
              <div className="border-t border-white/10 my-2" />
              <button
                onClick={() => {
                  handleLogout();
                  setMobileOpen(false);
                }}
                className="w-full flex items-center gap-3 px-5 py-3 text-sm font-bold text-donglyn hover:bg-white/5 transition text-left"
              >
                <i data-lucide="log-out" className="w-5" />
                Keluar
              </button>
            </>
          )}
        </div>

        {/* Footer Credit */}
        <div className="border-t border-white/10 px-5 py-4 flex-shrink-0 text-center">
          <p className="text-[10px] font-black tracking-[0.25em] text-white/90">CRAFTED BY</p>
          <p className="text-sm font-black tracking-wider text-donglyn mt-0.5">Vexalyn Dev</p>
        </div>
      </div>
    </>
  );
}
