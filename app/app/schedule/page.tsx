"use client";

import { useEffect, useState } from "react";
import PosterCard from "@/components/content/PosterCard";
import { SkeletonGrid } from "@/components/ui/States";
import { api } from "@/lib/api";
import type { ScheduleItem, PosterCardData } from "@/lib/types";

const DAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"];

export default function SchedulePage() {
  const [schedule, setSchedule] = useState<ScheduleItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeDay, setActiveDay] = useState(0);

  useEffect(() => {
    api.getSchedule().then((res) => setSchedule(res.schedule || [])).catch(() => {}).finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const today = new Date().getDay();
    setActiveDay(today === 0 ? 6 : today - 1);
  }, []);

  if (loading) {
    return (
      <div className="max-w-[1600px] mx-auto px-4 md:px-8 py-6">
        <h1 className="text-2xl md:text-3xl font-black text-white mb-6">Schedule</h1>
        <SkeletonGrid count={8} />
      </div>
    );
  }

  return (
    <div className="max-w-[1600px] mx-auto px-4 md:px-8 py-6">
      <h1 className="text-2xl md:text-3xl font-black text-white mb-6">Jadwal Rilis</h1>

      {/* Day Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-4 mb-6 scrollbar-hide">
        {DAYS.map((day, i) => {
          const item = schedule.find((s) => s.day === day);
          return (
            <button
              key={day}
              onClick={() => setActiveDay(i)}
              className={`flex-shrink-0 px-4 py-2 rounded-full text-sm font-bold transition-all ${
                activeDay === i
                  ? "bg-donglyn text-white"
                  : item
                    ? "bg-white/5 border border-white/10 text-white/70 hover:border-donglyn/40"
                    : "bg-white/5 border border-white/10 text-white/30 cursor-default"
              }`}
            >
              {day}
              {item && (
                <span className="ml-1.5 text-[10px] opacity-70">{item.items.length}</span>
              )}
            </button>
          );
        })}
      </div>

      {/* Content */}
      {(() => {
        const dayItems = schedule.find((s) => s.day === DAYS[activeDay])?.items || [];
        if (dayItems.length === 0) {
          return (
            <div className="text-center py-20">
              <div className="w-16 h-16 rounded-full bg-white/5 border border-white/10 flex items-center justify-center mx-auto mb-4">
                <i data-lucide="calendar" className="w-8 h-8 text-white/30" />
              </div>
              <p className="text-white/50">Tidak ada rilis untuk hari ini</p>
            </div>
          );
        }
        return (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
            {dayItems.map((item, i) => (
              <PosterCard key={`${item.id || i}-${item.url}`} data={item} index={i} />
            ))}
          </div>
        );
      })()}
    </div>
  );
}
