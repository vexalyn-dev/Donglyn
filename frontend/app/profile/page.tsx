"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import PosterCard from "@/components/content/PosterCard";
import { api } from "@/lib/api";
import type { UserData } from "@/lib/types";

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [username, setUsername] = useState("");
  const [bio, setBio] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api
      .getMe()
      .then((res: { logged_in: boolean; user: UserData | null }) => {
        if (!res.logged_in) {
          router.push("/login");
          return;
        }
        setUser(res.user);
        setUsername(res.user?.username || "");
        setBio(res.user?.bio || "");
      })
      .catch(() => router.push("/login"))
      .finally(() => setLoading(false));
  }, [router]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.updateProfile({ username, bio });
      setUser((prev) => (prev ? { ...prev, username, bio } : prev));
      setEditMode(false);
    } catch {
      // ignore
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 md:px-8 py-12">
        <div className="animate-pulse">
          <div className="h-32 bg-white/5 rounded-2xl mb-6" />
          <div className="flex items-end gap-4 -mt-8 mb-6">
            <div className="w-20 h-20 rounded-full bg-white/5 border-4 border-background" />
            <div className="flex-1 pb-2">
              <div className="h-6 bg-white/5 rounded w-1/3 mb-2" />
              <div className="h-4 bg-white/5 rounded w-1/2" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 md:px-8 py-12">
      {/* Banner */}
      <div className="h-32 rounded-2xl bg-gradient-to-r from-donglyn/20 to-purple-500/20 border border-white/10 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(229,9,20,.15),transparent)]" />
      </div>

      {/* Avatar + Info */}
      <div className="flex items-end gap-4 -mt-8 mb-8">
        <div className="w-20 h-20 rounded-full bg-background-card border-4 border-background flex items-center justify-center text-donglyn text-2xl font-black">
          {user?.username?.[0]?.toUpperCase() || "U"}
        </div>
        <div className="flex-1 pb-2">
          {editMode ? (
            <div className="space-y-2">
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm outline-none focus:border-donglyn/60"
                placeholder="Username"
              />
              <textarea
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm outline-none focus:border-donglyn/60 resize-none"
                placeholder="Bio (opsional)"
                rows={2}
              />
              <div className="flex gap-2">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="px-4 py-1.5 rounded-lg bg-donglyn text-white text-sm font-bold hover:bg-[#f40612] transition disabled:opacity-50"
                >
                  {saving ? "Menyimpan..." : "Simpan"}
                </button>
                <button
                  onClick={() => {
                    setEditMode(false);
                    setUsername(user?.username || "");
                    setBio(user?.bio || "");
                  }}
                  className="px-4 py-1.5 rounded-lg bg-white/10 text-white text-sm font-bold hover:bg-white/15 transition"
                >
                  Batal
                </button>
              </div>
            </div>
          ) : (
            <>
              <h1 className="text-xl font-black text-white">{user?.username || "User"}</h1>
              <p className="text-white/50 text-sm">{user?.email}</p>
              {user?.bio && <p className="text-white/60 text-sm mt-1">{user.bio}</p>}
              <button
                onClick={() => setEditMode(true)}
                className="mt-2 px-4 py-1.5 rounded-lg bg-white/5 border border-white/10 text-white text-xs font-bold hover:bg-white/10 transition"
              >
                Edit Profil
              </button>
            </>
          )}
        </div>
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { href: "/bookmark", label: "Bookmark", icon: "bookmark" },
          { href: "/riwayat", label: "Riwayat", icon: "history" },
          { href: "/profile", label: "Settings", icon: "settings" },
          { href: "#", label: "Keluar", icon: "log-out", action: true },
        ].map((item) => (
          <Link
            key={item.href}
            href={item.action ? "#" : item.href}
            onClick={(e) => {
              if (item.action) {
                e.preventDefault();
                api.logout().then(() => router.replace("/"));
              }
            }}
            className="flex flex-col items-center gap-2 p-4 rounded-xl bg-white/5 border border-white/10 hover:border-donglyn/30 hover:bg-donglyn/5 transition-all group"
          >
            <i data-lucide={item.icon} className="w-6 h-6 text-white/50 group-hover:text-donglyn transition-colors" />
            <span className="text-sm font-medium text-white/70 group-hover:text-white transition-colors">
              {item.label}
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
