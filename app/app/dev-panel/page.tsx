"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface DevStats {
  total_users: number;
  total_bookmarks: number;
  total_history: number;
  cache_size: number;
  uptime: string;
}

export default function DevPanelPage() {
  const [stats, setStats] = useState<DevStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getMe().then((res) => {
      if (!res.logged_in || !res.user?.is_dev_admin) {
        window.location.href = "/";
        return;
      }
      return api.devStats();
    }).then((res) => {
      if (res) setStats(res);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 md:px-8 py-12">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-white/5 rounded w-1/3" />
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-24 bg-white/5 rounded-xl" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 md:px-8 py-12">
      <h1 className="text-2xl font-black text-white mb-8">Developer Panel</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: "Total Users", value: stats?.total_users ?? 0, icon: "users" },
          { label: "Bookmarks", value: stats?.total_bookmarks ?? 0, icon: "bookmark" },
          { label: "History Items", value: stats?.total_history ?? 0, icon: "history" },
          { label: "Cache Size", value: `${(stats?.cache_size ?? 0).toFixed(1)} MB`, icon: "database" },
        ].map((stat) => (
          <div
            key={stat.label}
            className="bg-white/5 border border-white/10 rounded-xl p-4"
          >
            <div className="flex items-center gap-2 mb-2">
              <i data-lucide={stat.icon} className="w-5 h-5 text-donglyn" />
              <span className="text-white/50 text-xs font-medium">{stat.label}</span>
            </div>
            <p className="text-2xl font-black text-white">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="bg-white/5 border border-white/10 rounded-xl p-6">
        <h2 className="text-lg font-black text-white mb-4">Actions</h2>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={async () => {
              await api.devClearCache();
              window.location.reload();
            }}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-white/10 border border-white/20 text-white text-sm font-medium hover:bg-white/15 transition"
          >
            <i data-lucide="refresh-cw" className="w-4 h-4" />
            Clear Cache
          </button>
          <button
            onClick={async () => {
              await api.devRefreshScraper();
              alert("Scraper refreshed!");
            }}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-donglyn/20 border border-donglyn/40 text-donglyn text-sm font-medium hover:bg-donglyn/30 transition"
          >
            <i data-lucide="refresh-ccw" className="w-4 h-4" />
            Refresh Scraper
          </button>
          <button
            onClick={async () => {
              await api.devSyncAll();
              alert("Sync started!");
            }}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-white/10 border border-white/20 text-white text-sm font-medium hover:bg-white/15 transition"
          >
            <i data-lucide="sync" className="w-4 h-4" />
            Sync All
          </button>
        </div>
      </div>

      {/* Uptime */}
      <div className="mt-6 text-center text-white/30 text-xs">
        Uptime: {stats?.uptime || "N/A"}
      </div>
    </div>
  );
}
