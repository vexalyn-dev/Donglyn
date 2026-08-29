import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Detail Donghua | Donglyn",
  description: "Lihat detail donghua dan mulai streaming",
};

export default function DetailLayout({ children }: { children: React.ReactNode }) {
  return children;
}
