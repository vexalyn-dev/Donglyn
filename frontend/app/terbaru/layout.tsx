import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Beranda | Donglyn",
  description: "Pusat streaming donghua terlengkap dengan subtitle Indonesia",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return children;
}
