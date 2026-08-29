import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Search Donghua | Donglyn",
  description: "Cari donghua favoritmu di Donglyn",
};

export default function SearchLayout({ children }: { children: React.ReactNode }) {
  return children;
}
