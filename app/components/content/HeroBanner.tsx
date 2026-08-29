"use client";

import { useEffect, useRef } from "react";
import type { BannerItem } from "@/lib/types";

interface HeroBannerProps {
  banners: BannerItem[];
  loading?: boolean;
}

export default function HeroBanner({ banners, loading = false }: HeroBannerProps) {
  const swiperRef = useRef<HTMLDivElement>(null);
  const swiperInstance = useRef<any>(null);

  useEffect(() => {
    if (!swiperRef.current || !banners.length || loading) return;

    const initSwiper = async () => {
      const Swiper = (await import("swiper")).default;
      const { Navigation, Pagination, Autoplay } = await import("swiper/modules");

      Swiper.use([Navigation, Pagination, Autoplay]);

      if (swiperInstance.current) {
        swiperInstance.current.destroy();
      }

      swiperInstance.current = new Swiper(swiperRef.current!, {
        modules: [Navigation, Pagination, Autoplay],
        slidesPerView: 1,
        spaceBetween: 0,
        loop: true,
        autoplay: {
          delay: 5000,
          disableOnInteraction: false,
        },
        pagination: {
          el: ".swiper-pagination",
          clickable: true,
        },
        navigation: {
          nextEl: ".hero-next",
          prevEl: ".hero-prev",
        },
        speed: 800,
      });
    };

    initSwiper();

    return () => {
      if (swiperInstance.current) {
        swiperInstance.current.destroy();
      }
    };
  }, [banners, loading]);

  if (loading || banners.length === 0) {
    return (
      <div className="relative h-[50vh] md:h-[60vh] lg:h-[70vh] max-h-[600px] rounded-2xl overflow-hidden mx-4 md:mx-0">
        <div className="absolute inset-0 bg-white/5 animate-pulse rounded-2xl" />
      </div>
    );
  }

  return (
    <div className="relative mx-4 md:mx-0 rounded-2xl overflow-hidden" style={{ aspectRatio: "2.4/1" }}>
      {/* Swiper */}
      <div ref={swiperRef} className="swiper w-full h-full">
        <div className="swiper-wrapper">
          {banners.map((banner) => (
            <div key={banner.id} className="swiper-slide relative">
              {/* Background image */}
              <img
                src={banner.poster}
                alt={banner.title}
                className="absolute inset-0 w-full h-full object-cover"
                loading="eager"
                decoding="async"
              />

              {/* Gradient overlay */}
              <div
                className="absolute inset-0 bg-hero-gradient"
                style={{
                  background:
                    "linear-gradient(77deg, rgba(0,0,0,.85) 0%, rgba(0,0,0,.55) 45%, rgba(0,0,0,.15) 75%, transparent 90%), linear-gradient(to top, #141414 0%, transparent 50%)",
                }}
              />

              {/* Vignette */}
              <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_0%,rgba(0,0,0,.4)_100%)]" />

              {/* Content */}
              <div className="absolute inset-0 flex items-end pb-16 md:pb-24 px-6 md:px-12">
                <div className="max-w-xl">
                  {/* Badge */}
                  {banner.subtitle && (
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-donglyn/20 border border-donglyn/30 text-donglyn text-xs font-black tracking-wider mb-3">
                      <i data-lucide="zap" className="w-3 h-3" />
                      {banner.subtitle}
                    </div>
                  )}

                  {/* Title */}
                  <h1 className="text-2xl md:text-4xl lg:text-5xl font-black text-white leading-tight mb-3 drop-shadow-lg">
                    {banner.title}
                  </h1>

                  {/* Description */}
                  {banner.description && (
                    <p className="text-white/70 text-sm md:text-base line-clamp-2 mb-5 max-w-lg">
                      {banner.description}
                    </p>
                  )}

                  {/* CTAs */}
                  <div className="flex flex-wrap gap-3">
                    <a
                      href={`/detail?url=${encodeURIComponent(banner.url)}`}
                      className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-donglyn text-white font-black text-sm tracking-wide hover:bg-[#f40612] transition-all duration-200 hover:-translate-y-0.5 hover:shadow-[0_8px_24px_rgba(229,9,20,.4)]"
                    >
                      <i data-lucide="play" className="w-4 h-4 fill-current" />
                      MULAI STREAMING
                    </a>
                    <a
                      href={`/detail?url=${encodeURIComponent(banner.url)}`}
                      className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white/10 border border-white/20 text-white font-black text-sm tracking-wide hover:bg-white/15 transition-all duration-200 hover:-translate-y-0.5 backdrop-blur-sm"
                    >
                      <i data-lucide="info" className="w-4 h-4" />
                      JELAJAHI DONGHUA
                    </a>
                  </div>
                </div>
              </div>

              {/* Red ambient glow */}
              <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-donglyn/5 to-transparent pointer-events-none" />
            </div>
          ))}
        </div>

        {/* Pagination */}
        <div className="swiper-pagination" />

        {/* Navigation arrows */}
        <div className="hero-prev absolute top-1/2 -translate-y-1/2 left-4 w-10 h-10 rounded-full bg-black/50 border border-white/20 flex items-center justify-center text-white hover:bg-donglyn/80 transition-all cursor-pointer z-10">
          <i data-lucide="chevron-left" className="w-5 h-5" />
        </div>
        <div className="hero-next absolute top-1/2 -translate-y-1/2 right-4 w-10 h-10 rounded-full bg-black/50 border border-white/20 flex items-center justify-center text-white hover:bg-donglyn/80 transition-all cursor-pointer z-10">
          <i data-lucide="chevron-right" className="w-5 h-5" />
        </div>
      </div>
    </div>
  );
}
